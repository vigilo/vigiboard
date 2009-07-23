# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""Vigiboard Controller"""

import tg

from tg import config, expose, flash, require, request, redirect, \
                validate, tmpl_context

from tw.forms import validators 

from pylons.i18n import ugettext as _

from sqlalchemy import sql, asc

from vigicore.lib.base import TGController
from vigicore.model import DBSession

from vigicore.model import ServiceHautNiveau, HostGroups, \
        Events, EventHistory

from repoze.what.predicates import Any, not_anonymous

from vigiboard.widgets.edit_event import edit_event_status_options

from vigicore.controllers.userutils import get_user_groups
from vigiboard.controllers.vigiboardrequest import \
        VigiboardRequest

from vigicore.controllers.vigicore_controller import Vigicore_RootController

__all__ = ['RootController']

class RootController(Vigicore_RootController):
    
    """
    Le controller général de vigiboard
    """

    @expose()
    def process_form_errors (self, *argv, **kwargv):

        """
        Gestion des erreurs de validation : On affiche les erreurs
        puis on redirige vers la dernière page accédée.
        """
        flash(tmpl_context.form_errors, 'error')
        if request.environ.get('HTTP_REFERER') :
            redirect(request.environ.get('HTTP_REFERER'
                ).split(request.environ.get('HTTP_HOST'))[1])
        else :
            redirect('/')

    @validate(validators={'page':validators.Int(not_empty=False)},
            error_handler=process_form_errors)
    @expose('vigiboard.templates.vigiboard')
    @require(Any(not_anonymous(), msg="You need to be authenticated"))
    def index(self, page = 1, host = None, service = None, output = None,
            trouble_ticket=None):
            
        """
        Page d'accueil de Vigiboard. Elle affiche, suivant la page demandée (page 1 par
        defaut), la liste des évènements, rangé par ordre de prise en compte puis de sévérité.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param page: numéro de la page souhaité, commence à 1
        @param host: Si l'utilisateur souhaite sélectionner seulement certains
                     évènments suivant leur hôte, il peut placer une expression
                     ici en suivant la structure du LIKE en SQL
        @param service: Idem que host mais sur les services
        @param output: Idem que host mais sur le text explicatif
        @param trouble_ticket: Idem que host mais sur les tickets attribués
        """
        if page < 1 :
            page = 1

        events = VigiboardRequest()

        # Application des filtres si nécessaire
        if host :
            events.add_filter(Events.hostname.like('%%%s%%' % host))
        if service :
            events.add_filter(Events.servicename.like('%%%s%%' % service))
        if output :
            events.add_filter(Events.output.like('%%%s%%' % output))
        if trouble_ticket :
            events.add_filter(Events.trouble_ticket.like(
                '%%%s%%' % trouble_ticket))

        # Calcul des éléments à afficher et du nombre de pages possibles
        total_row = events.num_rows()
       
        item_per_page = int(tg.config['vigiboard_item_per_page'])

        if total_row <= item_per_page * (page-1) :
            page = 1
        id_first_row = item_per_page * (page-1)
        id_last_row = min(id_first_row + item_per_page, total_row)

        events.format_events(id_first_row, id_last_row)
        events.generate_tmpl_context() 

        return dict(
               events = events.events,
               id_first_row = id_first_row + 1,
               id_last_row = id_last_row,
               total_row = total_row,
               pages = range(1, (total_row / item_per_page) + 2),
               page = page,
               event_edit_status_options = edit_event_status_options,
               history = [],
               hist_error = False
            )
       
    @validate(validators={'idevent':validators.Int(not_empty=True)},
            error_handler=process_form_errors)
    @expose('json')
    @require(Any(not_anonymous(), msg=_("You need to be authenticated")))
    def history_dialog (self, idevent) :
        
        """
        JSon renvoyant les éléments pour l'affichage de la fenêtre de dialogue
        contenant des liens internes et externes.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param id: identifiant de l'évènement
        """
        
        # Obtention de données sur l'évènement et sur son historique
        events = DBSession.query(Events.severity, Events.idevent,
                        Events.hostname, Events.servicename
                 ).join(( HostGroups , Events.hostname == HostGroups.hostname )
                 ).filter(HostGroups.groupname.in_(get_user_groups())
                 ).filter(Events.idevent == idevent)[0]

        initial_state = DBSession.query(EventHistory
                 ).filter(EventHistory.idevent == idevent
                 ).order_by(asc(EventHistory.timestamp)
                 ).order_by(asc(EventHistory.type_action))

        if initial_state.count() > 0 :
            initial_state = initial_state[0].value
        else :
            initial_state = 0
        
        severity = { 0: _('None'), 1: _('OK'), 2: _('Suppressed'),
                3: _('Initial'), 4: _('Maintenance'), 5: _('Minor'),
                6: _('Major'), 7: _('Critical') }
        
        return dict(
                initial_state = severity[int(initial_state)],
                current_state = severity[events.severity],
                idevent = events.idevent,
                host = events.hostname,
                service = events.servicename,
                nagios_link = tg.config['vigiboard_links.nagios'] % \
                        {'idevent': events.idevent},
                metrology_link = tg.config['vigiboard_links.metrology'] % \
                        {'idevent': events.idevent},
                security_link = tg.config['vigiboard_links.security'] % \
                        {'idevent': events.idevent},
                servicetype_link = tg.config['vigiboard_links.servicetype'] % \
                        {'idevent': events.idevent}
            )

    @validate(validators={'idevent':validators.Int(not_empty=True)},
            error_handler=process_form_errors)
    @expose('vigiboard.templates.vigiboard')
    @require(Any(not_anonymous(), msg=_("You need to be authenticated")))
    def event(self, idevent):
        """
        Affichage de l'historique d'un évènement.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param idevent: identifiant de l'évènement souhaité
        """

        events = VigiboardRequest()
        events.add_filter(Events.idevent == idevent)
        
        # Vérification que l'évènement existe
        if events.num_rows() != 1 :
            flash(_('Error in DB'), 'error')
            redirect('/')
       
        events.format_events(0, 1)
        events.format_history()
        events.generate_tmpl_context() 

        return dict(
               events = events.events,
               id_first_row = 1,
               id_last_row = 1,
               total_row = 1,
               pages = [1],
               page = 1,
               event_edit_status_options = edit_event_status_options,
               history = events.hist,
               hist_error = True
            )

    @validate(validators={'host':validators.NotEmpty(),
        'service':validators.NotEmpty()}, error_handler=process_form_errors)
    @expose('vigiboard.templates.vigiboard')
    @require(Any(not_anonymous(), msg=_("You need to be authenticated")))
    def host_service(self, host, service):
        
        """
        Affichage de l'historique de l'ensemble des évènements correspondant au
        host et service demandé.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param host: Nom de l'hôte souhaité.
        @param service: Nom du service souhaité
        """

        events = VigiboardRequest()
        events.add_filter(Events.hostname == host,
                Events.servicename == service)
        
        # Vérification qu'il y a au moins 1 évènement qui correspond
        if events.num_rows() == 0 :
            redirect('/')
       
        events.format_events(0, events.num_rows())
        events.format_history()
        events.generate_tmpl_context() 

        return dict(
               events = events.events,
               id_first_row = 1,
               id_last_row = 1,
               total_row = 1,
               pages = [1],
               page = 1,
               event_edit_status_options = edit_event_status_options,
               history = events.hist,
               hist_error = True
            )

    @validate(validators={
        "id":validators.Regex(r'^[0-9]+(,[0-9]*)*,?$'),
        "trouble_ticket":validators.Regex(r'^[0-9]*$'),
        "status":validators.OneOf(['NoChange', 'None', 'Acknowledged',
                'AAClosed'])
        }, error_handler=process_form_errors)
    @require(Any(not_anonymous(), msg=_("You need to be authenticated")))
    def update(self,**krgv):
        
        """
        Mise à jour d'un évènement suivant les arguments passés.
        Cela peut être un changement de ticket ou un changement de statu.
        
        @param krgv['id']: Le ou les identifiants des évènements à traiter
        @param krgv['tt']: Nouveau numéro du ticket associé.
        @param krgv['status']: Nouveau status de/des évènements.
        """
        
        # Si l'utilisateur édite plusieurs évènements à la fois,
        # il nous faut chacun des identifiants

        ids = krgv['id'].split(',')
       
        if len(ids) > 1 :
            ids = ids[:-1]
        
        events = VigiboardRequest()
        events.add_filter(Events.idevent.in_(ids))
        
        # Vérification que au moins un des identifiants existe et est éditable
        if events.num_rows() <= 0 :
            flash(_('No access to this event'), 'error')
            redirect('/')
        
        # Modification des évènements et création d'un historique
        # pour chacun d'eux
        
        username = request.environ.get('repoze.who.identity'
                ).get('repoze.who.userid')

        for req in events.req :
            if isinstance(req,Events):
                event = req
            else:
                event = req[0]
            if krgv['trouble_ticket'] != '' :
                event.trouble_ticket = krgv['trouble_ticket']
                history = EventHistory(type_action = "Ticket change",
                    idevent = event.idevent, value = '', text = '',
                    username = username)
                DBSession.add(history)   
            if krgv['status'] != 'NoChange' :
                event.status = krgv['status']
                history = EventHistory(
                        type_action = "Acknowlegement change state",
                        idevent = event.idevent, value = '', text = '',
                        username = username)
                DBSession.add(history)
       
        flash(_('Updated successfully'))
	# Redirection vers la dernière page accédée
        redirect(request.environ.get('HTTP_REFERER').split(
            request.environ.get('HTTP_HOST')+tg.config['base_url_filter.base_url'])[1])


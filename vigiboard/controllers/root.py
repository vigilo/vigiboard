# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""Vigiboard Controller"""

from tg import expose, validate, require, flash, \
    tmpl_context, request, config, session, redirect
from tw.forms import validators 
from pylons.i18n import ugettext as _
from pylons.controllers.util import abort
from sqlalchemy import asc
from vigiboard.model import DBSession
from vigiboard.model import Event, EventHistory, EventsAggregate, \
                            Host, HostGroup, \
                            User
from repoze.what.predicates import Any, not_anonymous
from vigiboard.widgets.edit_event import edit_event_status_options
from vigiboard.controllers.vigiboardrequest import VigiboardRequest
from vigiboard.controllers.vigiboard_controller import VigiboardRootController

__all__ = ['RootController']

class RootController(VigiboardRootController):
    
    """
    Le controller général de vigiboard
    """

    def process_form_errors(self, *argv, **kwargv):
        """
        Gestion des erreurs de validation : On affiche les erreurs
        puis on redirige vers la dernière page accédée.
        """
        for k in tmpl_context.form_errors:
            flash("'%s': %s" % (k, tmpl_context.form_errors[k]), 'error')
        if request.environ.get('HTTP_REFERER') :
            redirect(request.environ.get('HTTP_REFERER'
                ).split(request.environ.get('HTTP_HOST'))[1])
        else :
            redirect('/')

    @expose('vigiboard.templates.vigiboard')
#    @require(Any(not_anonymous(), msg=_("You need to be authenticated")))
    def default(self, page = None, host = None, service = None, output = None,
            trouble_ticket=None, *argv, **krgv):
            
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
        if page is None:
            page = 1

        try:
            page = int(page)
        except ValueError:
            abort(404)

        if page < 1:
            page = 1

        events = VigiboardRequest()
        
        search = {'host':'', 'service':'', 'output':'', 'tt':''}
        # Application des filtres si nécessaire
        if host :
            search['host'] = host
            events.add_filter(Event.hostname.like('%%%s%%' % host))
        if service :
            search['service'] = service
            events.add_filter(Event.servicename.like('%%%s%%' % service))
        if output :
            search['output'] = output
            events.add_filter(Event.message.like('%%%s%%' % output))
        if trouble_ticket :
            search['tt'] = trouble_ticket
            events.add_filter(EventsAggregate.trouble_ticket.like(
                '%%%s%%' % trouble_ticket))

        # Calcul des éléments à afficher et du nombre de pages possibles
        total_rows = events.num_rows()
       
        item_per_page = int(config['vigiboard_item_per_page'])

        if total_rows <= item_per_page * (page-1) :
            page = 1
        id_first_row = item_per_page * (page-1)
        id_last_row = min(id_first_row + item_per_page, total_rows)

        events.format_events(id_first_row, id_last_row)
        events.generate_tmpl_context() 
        return dict(
               events = events.events,
               rows_info = {
                'id_first_row': id_first_row + 1,
                'id_last_row': id_last_row,
                'total_rows': total_rows,
               },
               pages = range(1, (total_rows / item_per_page) + 2),
               page = page,
               event_edit_status_options = edit_event_status_options,
               history = [],
               hist_error = False,
               plugin_context = events.context_fct,
               search = search,
            )
      
    @validate(validators={'idevent':validators.String(not_empty=True)},
            error_handler=process_form_errors)
    @expose('json')
    @require(Any(not_anonymous(), msg=_("You need to be authenticated")))
    def history_dialog(self, idevent):
        
        """
        JSon renvoyant les éléments pour l'affichage de la fenêtre de dialogue
        contenant des liens internes et externes.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param id: identifiant de l'évènement
        """

        # Obtention de données sur l'évènement et sur son historique
        username = request.environ.get('repoze.who.identity'
                    ).get('repoze.who.userid')
        user = User.by_user_name(username)

        event = DBSession.query(
                        EventsAggregate.severity,
                        Event.hostname,
                        Event.servicename,
                 ).join(
                    (Event, EventsAggregate.idcause == Event.idevent),
                    (HostGroup, Event.hostname == HostGroup.hostname),
                 ).filter(HostGroup.groupname.in_(user.groups)
                 ).filter(EventsAggregate.idcause == idevent).one()

        initial_state = DBSession.query(
                    EventHistory,
                 ).filter(EventHistory.idevent == idevent
                 ).order_by(asc(EventHistory.timestamp)
                 ).order_by(asc(EventHistory.type_action))

        if initial_state.count() > 0 :
            for i in initial_state:
                if i.value != '' and i.value is not None:
                    initial_state = i.value
                    break
        else :
            initial_state = 0

        severity = { 0: _('None'), 1: _('OK'), 2: _('Suppressed'),
                3: _('Initial'), 4: _('Maintenance'), 5: _('Minor'),
                6: _('Major'), 7: _('Critical') }
        eventdetails = {}
        for edname, edlink in \
                config['vigiboard_links.eventdetails'].iteritems():

            eventdetails[edname] = edlink[1] % {
                    'idevent': idevent,
                    'host': event.hostname,
                    'service': event.servicename
                    }

        return dict(
                initial_state = severity[int(initial_state)],
                current_state = severity[event.severity],
                idevent = idevent,
                host = event.hostname,
                service = event.servicename,
                eventdetails = eventdetails
            )

    @validate(validators={'idevent':validators.String(not_empty=True)},
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
        events.add_filter(EventsAggregate.idcause == idevent)
        
        # Vérification que l'évènement existe
        if events.num_rows() != 1 :
            flash(_('Error in DB'), 'error')
            redirect('/')
       
        events.format_events(0, 1)
        events.format_history()
        events.generate_tmpl_context() 

        return dict(
                    events = events.events,
                    rows_info = {
                        'id_first_row': 1,
                        'id_last_row': 1,
                        'total_rows': 1,
                    },
                    pages = [1],
                    page = 1,
                    event_edit_status_options = edit_event_status_options,
                    history = events.hist,
                    hist_error = True,
                    plugin_context = events.context_fct,
                    search = {
                        'host': None,
                        'service': None,
                        'output': None,
                        'tt': None
                    }
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
        events.add_filter(Event.hostname == host,
                Event.servicename == service)
        del events.filter[2]

        # Vérification qu'il y a au moins 1 évènement qui correspond
        if events.num_rows() == 0 :
            redirect('/')
       
        events.format_events(0, events.num_rows())
        events.format_history()
        events.generate_tmpl_context() 
        return dict(
                    events = events.events,
                    rows_info = {
                        'id_first_row': 1,
                        'id_last_row': 1,
                        'total_rows': 1,
                    },
                    pages = [1],
                    page = 1,
                    event_edit_status_options = edit_event_status_options,
                    history = events.hist,
                    hist_error = True,
                    plugin_context = events.context_fct,
                    search = {
                        'host': None,
                        'service': None,
                        'output': None,
                        'tt': None
                    }
                )

    @validate(validators={
        "id":validators.Regex(r'^[^,]+(,[^,]*)*,?$'),
        "trouble_ticket":validators.Regex(r'^[0-9]*$'),
        "status":validators.OneOf(['NoChange', 'None', 'Acknowledged',
                'AAClosed'])
        }, error_handler=process_form_errors)
    @require(Any(not_anonymous(), msg=_("You need to be authenticated")))
    def update(self,**krgv):
        
        """
        Mise à jour d'un évènement suivant les arguments passés.
        Cela peut être un changement de ticket ou un changement de statut.
        
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
        events.add_filter(EventsAggregate.idcause.in_(ids))
        
        # Vérification que au moins un des identifiants existe et est éditable
        if events.num_rows() <= 0 :
            flash(_('No access to this event'), 'error')
            redirect('/')
        
        # Modification des évènements et création d'un historique
        # pour chacun d'eux
        
        username = request.environ['repoze.who.identity']['repoze.who.userid']

        for req in events.req :
            if isinstance(req, EventsAggregate):
                event = req
            else:
                event = req[0]

            if krgv['trouble_ticket'] != '' :
                event.trouble_ticket = krgv['trouble_ticket']
                history = EventHistory(
                        type_action="Ticket change",
                        idevent=event.idcause,
                        value='',
                        text='',
                        username=username,
                    )
                DBSession.add(history)   

            if krgv['status'] != 'NoChange' :
                event.status = krgv['status']
                history = EventHistory(
                        type_action="Acknowlegement change state",
                        idevent=event.idcause,
                        value='',
                        text='',
                        username=username,
                    )
                DBSession.add(history)
       
        flash(_('Updated successfully'))
	# Redirection vers la dernière page accédée
        redirect(request.environ.get('HTTP_REFERER').split(
                    request.environ.get('HTTP_HOST') + \
                    config['base_url_filter.base_url'])[1])


    @validate(validators={"plugin_name":validators.OneOf(
        [i for [i,j] in config.get('vigiboard_plugins', [])])},
                error_handler = process_form_errors)
    @expose('json')
    def get_plugin_value(self, plugin_name, *arg, **krgv):
        """
        Permet aux plugins de pouvoir récupérer des valeurs Json
        """
        plugins = config['vigiboard_plugins']
        if plugins is None:
            return

        plugin = [i for i in plugins if i[0] == plugin_name][0]
        try:
            mypac = __import__(
                'vigiboard.controllers.vigiboard_plugin.' + plugin[0],
                globals(), locals(), [plugin[1]], -1)
            plug = getattr(mypac, plugin[1])()
            return plug.controller(*arg, **krgv)
        except:
            raise
    
#    @validate(validators= {"fontsize": validators.Int()},
#                    error_handler = process_form_errors)
    @expose('json')
    def set_fontsize(self, fontsize):
        """
        Save font size
        """
        session['fontsize'] = fontsize
        session.save()
        return dict(ret= 'ok')

    @validate(validators= {"refresh": validators.Int()},
            error_handler = process_form_errors)
    @expose('json')
    def set_refresh(self, refresh):
        """
        Save refresh time
        """
        session['refresh'] = refresh
        session.save()
        return dict(ret= 'ok')

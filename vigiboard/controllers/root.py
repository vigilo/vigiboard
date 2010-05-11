# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""Vigiboard Controller"""

from datetime import datetime
from time import mktime
import math

from tg.exceptions import HTTPNotFound, HTTPInternalServerError
from tg import expose, validate, require, flash, \
    tmpl_context, request, config, session, redirect
from tw.forms import validators
from pylons.i18n import ugettext as _
from pylons.i18n import lazy_ugettext as l_
from sqlalchemy import asc
from sqlalchemy.sql import func
from repoze.what.predicates import Any, All, in_group, \
                                    has_permission, not_anonymous
from formencode import validators, schema

from vigilo.models.session import DBSession
from vigilo.models.tables import Event, EventHistory, CorrEvent, Host, \
                                    SupItem, SupItemGroup, LowLevelService, \
                                    StateName
from vigilo.models.functions import sql_escape_like
from vigilo.models.tables.secondary_tables import EVENTSAGGREGATE_TABLE

from vigilo.turbogears.controllers.autocomplete import AutoCompleteController
from vigilo.turbogears.helpers import get_current_user

from vigiboard.controllers.vigiboardrequest import VigiboardRequest
from vigiboard.controllers.vigiboard_controller import VigiboardRootController
from vigiboard.widgets.edit_event import edit_event_status_options

__all__ = ('RootController', 'get_last_modification_timestamp', 
           'date_to_timestamp')

# pylint: disable-msg=R0201
class RootController(VigiboardRootController):
    """
    Le controller général de vigiboard
    """
    autocomplete = AutoCompleteController()

    # Prédicat pour la restriction de l'accès aux interfaces.
    # L'utilisateur doit avoir la permission "vigiboard-read"
    # ou appartenir au groupe "managers" pour accéder à VigiBoard.
    access_restriction = All(
        not_anonymous(msg=l_("You need to be authenticated")),
        Any(in_group('managers'),
            has_permission('vigiboard-read'),
            msg=l_("You don't have read access to VigiBoard"))
    )

    def process_form_errors(self, *argv, **kwargv):
        """
        Gestion des erreurs de validation : On affiche les erreurs
        puis on redirige vers la dernière page accédée.
        """
        for k in tmpl_context.form_errors:
            flash("'%s': %s" % (k, tmpl_context.form_errors[k]), 'error')
        redirect(request.environ.get('HTTP_REFERER', '/'))

    @expose('json')
    def handle_validation_errors_json(self, *args, **kwargs):
        kwargs['errors'] = tmpl_context.form_errors
        return dict(kwargs)
    
    class DefaultSchema(schema.Schema):
        page = validators.Int(min=1, if_missing=1, if_invalid=1)
        supitemgroup = validators.String(if_missing=None)
        host = validators.String(if_missing=None)
        service = validators.String(if_missing=None)
        output = validators.String(if_missing=None)
        trouble_ticket = validators.String(if_missing=None)
        from_date = validators.String(if_missing=None)
        to_date = validators.String(if_missing=None)

    @validate(
        validators=DefaultSchema(),
        error_handler = process_form_errors)
    @expose('events_table.html')
    @require(access_restriction)
    def default(self, page, supitemgroup, host, service,
                output, trouble_ticket, from_date, to_date):
        """
        Page d'accueil de Vigiboard. Elle affiche, suivant la page demandée
        (page 1 par defaut), la liste des événements, rangés par ordre de prise
        en compte, puis de sévérité.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param page: Numéro de la page souhaitée, commence à 1
        @param host: Si l'utilisateur souhaite sélectionner seulement certains
                     événements suivant leur hôte, il peut placer une expression
                     ici en suivant la structure du LIKE en SQL
        @param service: Idem que host mais sur les services
        @param output: Idem que host mais sur le text explicatif
        @param trouble_ticket: Idem que host mais sur les tickets attribués

        Cette méthode permet de satisfaire les exigences suivantes : 
        - VIGILO_EXIG_VIGILO_BAC_0040, 
        - VIGILO_EXIG_VIGILO_BAC_0070,
        - VIGILO_EXIG_VIGILO_BAC_0100,
        """
        user = get_current_user()
        aggregates = VigiboardRequest(user)
        aggregates.add_table(
            CorrEvent,
            aggregates.items.c.hostname,
            aggregates.items.c.servicename
        )
        aggregates.add_join((Event, CorrEvent.idcause == Event.idevent))
        aggregates.add_join((aggregates.items, 
            Event.idsupitem == aggregates.items.c.idsupitem))
        aggregates.add_order_by(asc(aggregates.items.c.hostname))
        
        search = {
            'host': '',
            'service': '',
            'output': '',
            'tt': '',
            'from_date': '',
            'to_date': '',
            'supitemgroup': '',
        }

        # Application des filtres si nécessaire
        if supitemgroup:
            search['supitemgroup'] = supitemgroup
            supitemgroup = sql_escape_like(supitemgroup)
            aggregates.add_join((SupItemGroup, SupItemGroup.idgroup == \
                aggregates.items.c.idsupitemgroup))
            aggregates.add_filter(
                SupItemGroup.name.ilike('%%%s%%' % supitemgroup))

        if host:
            search['host'] = host
            host = sql_escape_like(host)
            aggregates.add_filter(aggregates.items.c.hostname.ilike(
                '%%%s%%' % host))

        if service:
            search['service'] = service
            service = sql_escape_like(service)
            aggregates.add_filter(aggregates.items.c.servicename.ilike(
                '%%%s%%' % service))

        if output:
            search['output'] = output
            output = sql_escape_like(output)
            aggregates.add_filter(Event.message.ilike('%%%s%%' % output))

        if trouble_ticket:
            search['tt'] = trouble_ticket
            trouble_ticket = sql_escape_like(trouble_ticket)
            aggregates.add_filter(CorrEvent.trouble_ticket.ilike(
                '%%%s%%' % trouble_ticket))

        if from_date:
            search['from_date'] = from_date
            try:
                # TRANSLATORS: Format de date et heure.
                from_date = datetime.strptime(
                    from_date, _('%Y-%m-%d %I:%M:%S %p'))
            except ValueError:
                # On ignore silencieusement la date invalide reçue.
                pass
            else:
                aggregates.add_filter(CorrEvent.timestamp_active >= from_date)

        if to_date:
            search['to_date'] = to_date
            try:
                # TRANSLATORS: Format de date et heure.
                to_date = datetime.strptime(
                    to_date, _('%Y-%m-%d %I:%M:%S %p'))
            except ValueError:
                # On ignore silencieusement la date invalide reçue.
                pass
            else:
                aggregates.add_filter(CorrEvent.timestamp_active <= to_date)

        # Calcul des éléments à afficher et du nombre de pages possibles
        total_rows = aggregates.num_rows()
        items_per_page = int(config['vigiboard_items_per_page'])

        # Si le numéro de page dépasse le nombre de pages existantes,
        # on redirige automatiquement vers la 1ère page.
        if total_rows and items_per_page * (page-1) > total_rows:
            redirect('/', page=1, **search)

        id_first_row = items_per_page * (page-1)
        id_last_row = min(id_first_row + items_per_page, total_rows)

        aggregates.format_events(id_first_row, id_last_row)
        aggregates.generate_tmpl_context()

        nb_pages = int(math.ceil(total_rows / (items_per_page + 0.0)))
        if not total_rows:
            id_first_row = 0
        else:
            id_first_row += 1

        return dict(
            hostname = None,
            servicename = None,
            events = aggregates.events,
            plugins = get_plugins_instances(),
            rows_info = {
                'id_first_row': id_first_row,
                'id_last_row': id_last_row,
                'total_rows': total_rows,
            },
            nb_pages = nb_pages,
            page = page,
            event_edit_status_options = edit_event_status_options,
            search = search,
            refresh_times = config['vigiboard_refresh_times'],
        )


    class MaskedEventsSchema(schema.Schema):
        idcorrevent = validators.Int(not_empty=True)
        page = validators.Int(min=1, if_missing=1, if_invalid=1)

    @validate(
        validators=MaskedEventsSchema(),
        error_handler = process_form_errors)
    @expose('raw_events_table.html')
    @require(access_restriction)
    def masked_events(self, idcorrevent, page):
        """
        Affichage de la liste des événements bruts masqués dans un
        événement corrélé (agrégés).

        @param idevent: identifiant de l'événement souhaité
        """
        user = get_current_user()

        # Récupère la liste des événements masqués de l'événement
        # corrélé donné par idcorrevent.
        events = VigiboardRequest(user, False)
        events.add_table(
            Event,
            events.items.c.hostname,
            events.items.c.servicename,
        )
        events.add_join((EVENTSAGGREGATE_TABLE, \
            EVENTSAGGREGATE_TABLE.c.idevent == Event.idevent))
        events.add_join((CorrEvent, CorrEvent.idcorrevent == \
            EVENTSAGGREGATE_TABLE.c.idcorrevent))
        events.add_join((events.items, 
            Event.idsupitem == events.items.c.idsupitem))
        events.add_filter(Event.idevent != CorrEvent.idcause)
        events.add_filter(CorrEvent.idcorrevent == idcorrevent)

        # Récupère l'instance de SupItem associé à la cause de
        # l'événement corrélé. Cette instance est utilisé pour
        # obtenir le nom d'hôte/service auquel la cause est
        # rattachée (afin de fournir un contexte à l'utilisateur).
        hostname = None
        servicename = None
        cause_supitem = DBSession.query(
                SupItem,
            ).join(
                (Event, Event.idsupitem == SupItem.idsupitem),
                (EVENTSAGGREGATE_TABLE, EVENTSAGGREGATE_TABLE.c.idevent ==
                    Event.idevent),
                (CorrEvent, CorrEvent.idcorrevent ==
                    EVENTSAGGREGATE_TABLE.c.idcorrevent),
            ).filter(CorrEvent.idcorrevent == idcorrevent
            ).filter(Event.idevent == CorrEvent.idcause
            ).one()

        if isinstance(cause_supitem, LowLevelService):
            hostname = cause_supitem.host.name
            servicename = cause_supitem.servicename
        elif isinstance(cause_supitem, Host):
            hostname = cause_supitem.name

        # Vérification que l'événement existe
        total_rows = events.num_rows()
        if total_rows < 1:
            flash(_('No masked event or access denied'), 'error')
            redirect('/')

        # Calcul des éléments à afficher et du nombre de pages possibles
        items_per_page = int(config['vigiboard_items_per_page'])

        id_first_row = items_per_page * (page-1)
        id_last_row = min(id_first_row + items_per_page, total_rows)

        events.format_events(id_first_row, id_last_row)
        events.generate_tmpl_context()

        nb_pages = int(math.ceil(total_rows / (items_per_page + 0.0)))
        if not total_rows:
            id_first_row = 0
        else:
            id_first_row += 1

        return dict(
            idcorrevent = idcorrevent,
            hostname = hostname,
            servicename = servicename,
            events = events.events,
            plugins = get_plugins_instances(),
            rows_info = {
                'id_first_row': id_first_row,
                'id_last_row': id_last_row,
                'total_rows': total_rows,
            },
            nb_pages = nb_pages,
            page = page,
            search = {
                'host': '',
                'service': '',
                'output': '',
                'tt': '',
                'from_date': '',
                'to_date': '',
                'supitemgroup': '',
            },
           refresh_times=config['vigiboard_refresh_times'],
        )


    class EventSchema(schema.Schema):
        idevent = validators.Int(not_empty=True)
        page = validators.Int(min=1, if_missing=1, if_invalid=1)

    @validate(
        validators=EventSchema(),
        error_handler = process_form_errors)
    @expose('history_table.html')
    @require(access_restriction)
    def event(self, idevent, page):
        """
        Affichage de l'historique d'un événement brut.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param idevent: identifiant de l'événement brut souhaité.
        @type idevent: C{int}

        Cette méthode permet de satisfaire
        l'exigence VIGILO_EXIG_VIGILO_BAC_0080.
        """
        if not page:
            page = 1

        user = get_current_user()
        events = VigiboardRequest(user, False)
        events.add_table(
            Event,
            events.items.c.hostname.label('hostname'),
            events.items.c.servicename.label('servicename'),
        )
        events.add_join((EVENTSAGGREGATE_TABLE, \
            EVENTSAGGREGATE_TABLE.c.idevent == Event.idevent))
        events.add_join((CorrEvent, CorrEvent.idcorrevent == \
            EVENTSAGGREGATE_TABLE.c.idcorrevent))
        events.add_join((events.items, 
            Event.idsupitem == events.items.c.idsupitem))
        events.add_filter(Event.idevent == idevent)

        if events.num_rows() != 1:
            flash(_('No such event or access denied'), 'error')
            redirect('/')

        events.format_events(0, 1)
        events.generate_tmpl_context()
        history = events.format_history()

        total_rows = history.count()
        items_per_page = int(config['vigiboard_items_per_page'])

        id_first_row = items_per_page * (page-1)
        id_last_row = min(id_first_row + items_per_page, total_rows)

        history_entries = history[id_first_row : id_last_row]

        nb_pages = int(math.ceil(total_rows / (items_per_page + 0.0)))
        if not total_rows:
            id_first_row = 0
        else:
            id_first_row += 1

        event = events.req[0]

        return dict(
            idevent = idevent,
            hostname = event.hostname,
            servicename = event.servicename,
            plugins = get_plugins_instances(),
            rows_info = {
                'id_first_row': id_first_row,
                'id_last_row': id_last_row,
                'total_rows': total_rows,
            },
            nb_pages = nb_pages,
            page = page,
            history = history_entries,
            search = {
                'host': '',
                'service': '',
                'output': '',
                'tt': '',
                'from_date': '',
                'to_date': '',
                'supitemgroup': '',
            },
           refresh_times=config['vigiboard_refresh_times'],
        )


    class ItemSchema(schema.Schema):
        page = validators.Int(min=1, if_missing=1, if_invalid=1)
        host = validators.String(not_empty=True)
        service = validators.String(if_missing=None)

    @validate(
        validators=ItemSchema(),
        error_handler = process_form_errors)
    @expose('events_table.html')
    @require(access_restriction)
    def item(self, page, host, service):
        """
        Affichage de l'historique de l'ensemble des événements corrélés
        jamais ouverts sur l'hôte / service demandé.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param host: Nom de l'hôte souhaité.
        @param service: Nom du service souhaité

        Cette méthode permet de satisfaire
        l'exigence VIGILO_EXIG_VIGILO_BAC_0080.
        """
        idsupitem = SupItem.get_supitem(host, service)

        user = get_current_user()
        aggregates = VigiboardRequest(user, False)
        aggregates.add_table(
            CorrEvent,
            aggregates.items.c.hostname,
            aggregates.items.c.servicename,
        )
        aggregates.add_join((Event, CorrEvent.idcause == Event.idevent))
        aggregates.add_join((aggregates.items, 
            Event.idsupitem == aggregates.items.c.idsupitem))
        aggregates.add_filter(aggregates.items.c.idsupitem == idsupitem)

        # Vérification qu'il y a au moins 1 événement qui correspond
        total_rows = aggregates.num_rows()
        if not total_rows:
            flash(_('No access to this host/service or no event yet'), 'error')
            redirect('/')

        items_per_page = int(config['vigiboard_items_per_page'])

        id_first_row = items_per_page * (page-1)
        id_last_row = min(id_first_row + items_per_page, total_rows)

        aggregates.format_events(id_first_row, id_last_row)
        aggregates.generate_tmpl_context()

        nb_pages = int(math.ceil(total_rows / (items_per_page + 0.0)))
        if not total_rows:
            id_first_row = 0
        else:
            id_first_row += 1
        
        return dict(
            hostname = host,
            servicename = service,
            events = aggregates.events,
            plugins = get_plugins_instances(),
            rows_info = {
                'id_first_row': id_first_row,
                'id_last_row': id_last_row,
                'total_rows': total_rows,
            },
            nb_pages = nb_pages,
            page = page,
            event_edit_status_options = edit_event_status_options,
            search = {
                'host': '',
                'service': '',
                'output': '',
                'tt': '',
                'from_date': '',
                'to_date': '',
                'supitemgroup': '',
            },
            refresh_times=config['vigiboard_refresh_times'],
        )


    class UpdateSchema(schema.Schema):
        id = validators.Regex(r'^[0-9]+(,[0-9]+)*,?$')
        last_modification = validators.Number(not_empty=True)
        trouble_ticket = validators.String(if_missing='')
        ack = validators.OneOf(
            [unicode(s[0]) for s in edit_event_status_options],
            not_empty=True)

    @validate(
        validators=UpdateSchema(),
        error_handler = process_form_errors)
    @require(
        All(
            not_anonymous(msg=l_("You need to be authenticated")),
            Any(in_group('managers'),
                has_permission('vigiboard-write'),
                msg=l_("You don't have write access to VigiBoard"))
        ))
    @expose()
    def update(self, id, last_modification, trouble_ticket, ack):
        """
        Mise à jour d'un événement suivant les arguments passés.
        Cela peut être un changement de ticket ou un changement de statut.
        
        @param id: Le ou les identifiants des événements à traiter
        @param last_modification: La date de la dernière modification
            dont l'utilisateur est au courant.
        @param trouble_ticket: Nouveau numéro du ticket associé.
        @param ack: Nouvel état d'acquittement des événements sélectionnés.

        Cette méthode permet de satisfaire les exigences suivantes : 
        - VIGILO_EXIG_VIGILO_BAC_0020,
        - VIGILO_EXIG_VIGILO_BAC_0060,
        - VIGILO_EXIG_VIGILO_BAC_0110.
        """

        # On vérifie que des identifiants ont bien été transmis via
        # le formulaire, et on informe l'utilisateur le cas échéant.
        if id is None:
            flash(_('No event has been selected'), 'warning')
            raise redirect(request.environ.get('HTTP_REFERER', '/'))

        # Le filtre permet d'éliminer les chaines vides contenues dans le
        # tableau ('a,b,' -> split -> ['a','b',''] -> filter -> ['a','b']).
        ids = map(int, filter(len, id.split(',')))

        # Si l'utilisateur édite plusieurs événements à la fois,
        # il nous faut chacun des identifiants

        user = get_current_user()
        events = VigiboardRequest(user)
        events.add_table(CorrEvent)
        events.add_join((Event, CorrEvent.idcause == Event.idevent))
        events.add_join((events.items, 
            Event.idsupitem == events.items.c.idsupitem))
        events.add_filter(CorrEvent.idcorrevent.in_(ids))
        
        events.generate_request()
        idevents = [cause.idcause for cause in events.req]

        # Si des changements sont survenus depuis que la 
        # page est affichée, on en informe l'utilisateur.
        last_modification = datetime.fromtimestamp(last_modification)
        cur_last_modification = get_last_modification_timestamp(idevents, None)
        if cur_last_modification and last_modification < cur_last_modification:
            flash(_('Changes have occurred since the page was last displayed, '
                    'your changes HAVE NOT been saved.'), 'warning')
            raise redirect(request.environ.get('HTTP_REFERER', '/'))

        # Vérification que au moins un des identifiants existe et est éditable
        if not events.num_rows():
            flash(_('No access to this event'), 'error')
            redirect('/')
        
        # Modification des événements et création d'un historique
        # pour chacun d'eux.
        for req in events.req:
            event = req

            if trouble_ticket and trouble_ticket != event.trouble_ticket:
                history = EventHistory(
                        type_action="Ticket change",
                        idevent=event.idcause,
                        value=unicode(trouble_ticket),
                        text="Changed trouble ticket from '%s' to '%s'" % (
                            event.trouble_ticket, trouble_ticket
                        ),
                        username=user.user_name,
                        timestamp=datetime.now(),
                    )
                DBSession.add(history)   
                event.trouble_ticket = trouble_ticket

            # Changement du statut d'acquittement.
            if ack != u'NoChange':
                # Pour forcer l'acquittement d'un événement,
                # il faut en plus avoir la permission
                # "vigiboard-admin".
                if ack == u'Forced':
                    condition = Any(
                        in_group('managers'),
                        has_permission('vigiboard-admin'),
                        msg=l_("You don't have administrative access "
                                "to VigiBoard"))
                    try:
                        condition.check_authorization(request.environ)
                    except NotAuthorizedError, e:
                        reason = unicode(e)
                        flash(reason, 'error')
                        raise redirect(request.environ.get('HTTP_REFERER', '/'))
                    else:
                        ack = u'AAClosed'
                        # On met systématiquement l'état à "OK", même s'il
                        # s'agit d'un hôte. Techniquement, c'est incorrect,
                        # mais comme on fait ça pour masquer l'événement...
                        event.cause.current_state = \
                            StateName.statename_to_value(u'OK')

                history = EventHistory(
                        type_action="Acknowledgement change state",
                        idevent=event.idcause,
                        value=ack,
                        text="Changed acknowledgement status "
                            "from '%s' to '%s'" % (
                            event.status, ack
                        ),
                        username=user.user_name,
                        timestamp=datetime.now(),
                    )
                DBSession.add(history)
                event.status = ack

        DBSession.flush()
        flash(_('Updated successfully'))
        redirect(request.environ.get('HTTP_REFERER', '/'))


    class GetPluginValueSchema(schema.Schema):
        idcorrevent = validators.Int(not_empty=True)
        plugin_name = validators.OneOf(
            [unicode(i[0]) for i in config.get('vigiboard_plugins', [])],
            not_empty=True, hideList=True)
        # Permet de passer des paramètres supplémentaires au plugin.
        allow_extra_fields = True

    @validate(
        validators=GetPluginValueSchema(),
        error_handler = handle_validation_errors_json)
    @expose('json')
    @require(access_restriction)
    def get_plugin_value(self, idcorrevent, plugin_name, *arg, **krgv):
        """
        Permet de récupérer la valeur d'un plugin associée à un CorrEvent
        donné via JSON.
        """
        plugins = config.get('vigiboard_plugins', {})
        # Permet de vérifier si l'utilisateur a bien les permissions
        # pour accéder à cet événement et si l'événement existe.
        user = get_current_user()
        events = VigiboardRequest(user, False)
        events.add_table(CorrEvent.idcorrevent)
        events.add_join((Event, CorrEvent.idcause == Event.idevent))
        events.add_join((events.items, 
            Event.idsupitem == events.items.c.idsupitem))
        events.add_filter(CorrEvent.idcorrevent == idcorrevent)

        # Pas d'événement ou permission refusée. On ne distingue pas
        # les 2 cas afin d'éviter la divulgation d'informations.
        if not events.num_rows():
            raise HTTPNotFound(_('No such incident or insufficient '
                                'permissions'))

        plugin_class = [p[1] for p in plugins if p[0] == plugin_name]
        if not plugin_class:
            raise HTTPNotFound(_('No such plugin'))

        plugin_class = plugin_class[0]
        try:
            mypac = __import__(
                'vigiboard.controllers.plugins.' + plugin_name,
                globals(), locals(), [plugin_class], -1)
            plugin = getattr(mypac, plugin_class)
            if callable(plugin):
                return plugin().get_value(idcorrevent, *arg, **krgv)
            raise HTTPInternalServerError(_('Not a valid plugin'))
        except ImportError:
            raise HTTPInternalServerError(_('Plugin could not be loaded'))

    @validate(validators={
        "fontsize": validators.Regex(
            r'[0-9]+(pt|px|em|%)',
            regexOps = ('I',)
        )}, error_handler = handle_validation_errors_json)
    @expose('json')
    def set_fontsize(self, fontsize):
        """Enregistre la taille de la police dans les préférences."""
        session['fontsize'] = fontsize
        session.save()
        return dict()

    @validate(validators={"refresh": validators.Int()},
            error_handler = handle_validation_errors_json)
    @expose('json')
    def set_refresh(self, refresh):
        """Enregistre le temps de rafraichissement dans les préférences."""
        session['refresh'] = refresh
        session.save()
        return dict()

    @expose('json')
    def set_theme(self, theme):
        """Enregistre le thème à utiliser dans les préférences."""
        # On sauvegarde l'ID du thème sans vérifications
        # car les thèmes (styles CSS) sont définies dans
        # les packages de thèmes (ex: vigilo-themes-default).
        # La vérification de la valeur est faite dans les templates.
        session['theme'] = theme
        session.save()
        return dict()
    
def get_last_modification_timestamp(event_id_list, 
                                    value_if_none=datetime.now()):
    """
    Récupère le timestamp de la dernière modification 
    opérée sur l'un des événements dont l'identifiant
    fait partie de la liste passée en paramètre.
    """
    last_modification_timestamp = DBSession.query(
                                func.max(EventHistory.timestamp),
                         ).filter(EventHistory.idevent.in_(event_id_list)
                         ).scalar()
    if not last_modification_timestamp:
        if not value_if_none:
            return None
        else:
            last_modification_timestamp = value_if_none
    return datetime.fromtimestamp(mktime(
        last_modification_timestamp.timetuple()))

def get_plugins_instances():
    """
    Renvoie une liste d'instances de plugins pour VigiBoard.

    @return: Liste de tuples contenant le nom du plugin
        et l'instance associée.
    @rtype: C{list} of C{tuple}
    """
    plugins = config.get('vigiboard_plugins', [])
    plugins_instances = []
    for (plugin_name, plugin_class) in plugins:
        try:
            mypac = __import__(
                'vigiboard.controllers.plugins.' + plugin_name,
                globals(), locals(), [plugin_class], -1)
            plugin = getattr(mypac, plugin_class)
            if callable(plugin):
                plugins_instances.append((plugin_name, plugin()))
        except ImportError:
            pass
    return plugins_instances


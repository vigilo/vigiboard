# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2020 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""VigiBoard Controller"""

import calendar
import gettext
import os.path
from datetime import datetime

from pkg_resources import resource_filename, working_set

from tg.exceptions import HTTPNotFound
from tg import expose, validate, require, flash, url, \
    tmpl_context, request, response, config, session, redirect
from tg.support import paginate
from formencode import validators, schema
from tg.i18n import ugettext as _, lazy_ugettext as l_, get_lang
from sqlalchemy import asc
from sqlalchemy.sql import func
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import or_
from tg.predicates import Any, All, NotAuthorizedError, \
                            has_permission, not_anonymous

from vigilo.models.session import DBSession
from vigilo.models.tables import Event, EventHistory, CorrEvent, Host, \
                                    SupItem, SupItemGroup, LowLevelService, \
                                    StateName, State, DataPermission
from vigilo.models.tables.grouphierarchy import GroupHierarchy
from vigilo.models.tables.secondary_tables import EVENTSAGGREGATE_TABLE, \
        USER_GROUP_TABLE, SUPITEM_GROUP_TABLE

from vigilo.turbogears.controllers.auth import AuthController
from vigilo.turbogears.controllers.selfmonitoring import SelfMonitoringController
from vigilo.turbogears.controllers.custom import CustomController
from vigilo.turbogears.controllers.error import ErrorController
from vigilo.turbogears.controllers.autocomplete import AutoCompleteController
from vigilo.turbogears.controllers.proxy import ProxyController
from vigilo.turbogears.controllers.i18n import I18nController
from vigilo.turbogears.controllers.api.root import ApiRootController
from vigilo.turbogears.helpers import get_current_user

from vigiboard.controllers.vigiboardrequest import VigiboardRequest
from vigiboard.controllers.feeds import FeedsController
from vigiboard.controllers.silence import SilenceController

from vigiboard.lib import export_csv, dateformat
from vigiboard.widgets.edit_event import edit_event_status_options, \
                                            EditEventForm
from vigiboard.widgets.search_form import create_search_form
import logging

LOGGER = logging.getLogger(__name__)

__all__ = ('RootController', 'get_last_modification_timestamp',
           'date_to_timestamp')

# pylint: disable-msg=R0201,W0613,W0622
# R0201: Method could be a function
# W0613: Unused arguments: les arguments sont la query-string
# W0622: Redefining built-in 'id': élément de la query-string

class RootController(AuthController, SelfMonitoringController, I18nController):
    """
    Le controller général de vigiboard
    """
    _tickets = None
    _use_index_fallback = True

    error = ErrorController()
    autocomplete = AutoCompleteController()
    nagios = ProxyController('nagios', '/nagios/',
        not_anonymous(l_('You need to be authenticated')))
    api = ApiRootController()
    feeds = FeedsController()
    silence = SilenceController()
    custom = CustomController()

    # Prédicat pour la restriction de l'accès aux interfaces.
    # L'utilisateur doit avoir la permission "vigiboard-access"
    # ou appartenir au groupe "managers" pour accéder à VigiBoard.
    access_restriction = All(
        not_anonymous(msg=l_("You need to be authenticated")),
        Any(config.is_manager,
            has_permission('vigiboard-access'),
            msg=l_("You don't have access to VigiBoard"))
    )

    def process_form_errors(self, *argv, **kwargv):
        """
        Gestion des erreurs de validation : on affiche les erreurs
        puis on redirige vers la dernière page accédée.
        """
        for k in tmpl_context.form_errors:
            flash("'%s': %s" % (k, tmpl_context.form_errors[k]), 'error')
        redirect(request.environ.get('HTTP_REFERER', '/'))

    @expose('json')
    def handle_validation_errors_json(self, *args, **kwargs):
        kwargs['errors'] = tmpl_context.form_errors
        return dict(kwargs)

    def __init__(self, *args, **kwargs):
        """Initialisation du contrôleur."""
        super(RootController, self).__init__(*args, **kwargs)
        # Si un module de gestion des tickets a été indiqué dans
        # le fichier de configuration, on tente de le charger.
        if config.get('tickets.plugin'):
            plugins = working_set.iter_entry_points('vigiboard.tickets', config['tickets.plugin'])
            if plugins:
                # La classe indiquée par la première valeur de l'itérateur
                # correspond au plugin que l'on veut instancier.
                pluginCls = plugins.next().load()
                self._tickets = pluginCls()

    class IndexSchema(schema.Schema):
        """Schéma de validation de la méthode index."""
        # Si on ne passe pas le paramètre "page" ou qu'on passe une valeur
        # invalide ou pas de valeur du tout, alors on affiche la 1ère page.
        page = validators.Int(
            min=1,
            if_missing=1,
            if_invalid=1,
            not_empty=True
        )

        # Paramètres de tri
        sort = validators.UnicodeString(if_missing='')
        order = validators.OneOf(['asc', 'desc'], if_missing='asc')

        # Le fait de chaîner la validation avec le formulaire de recherche
        # permet de convertir les critères de recherche vers leur type.
        chained_validators = [create_search_form.validator]

        allow_extra_fields = True

    @validate(
        validators=IndexSchema(),
        error_handler = process_form_errors)
    @expose('events_table.html')
    @require(access_restriction)
    def index(self, page=None, sort=None, order=None, **search):
        """
        Page d'accueil de Vigiboard. Elle affiche, suivant la page demandée
        (page 1 par defaut), la liste des événements, rangés par ordre de prise
        en compte, puis de sévérité.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param page: Numéro de la page souhaitée, commence à 1
        @type page: C{int}
        @param sort: Colonne de tri
        @type sort: C{str} or C{None}
        @param order: Ordre du tri (asc ou desc)
        @type order: C{str} or C{None}
        @param search: Dictionnaire contenant les critères de recherche.
        @type search: C{dict}

        Cette méthode permet de satisfaire les exigences suivantes :
            - VIGILO_EXIG_VIGILO_BAC_0040,
            - VIGILO_EXIG_VIGILO_BAC_0070,
            - VIGILO_EXIG_VIGILO_BAC_0100,
        """

        # Auto-supervision
        self.get_failures()

        user = get_current_user()
        aggregates = VigiboardRequest(user, search=search, sort=sort, order=order)

        aggregates.add_table(
            CorrEvent,
            aggregates.items.c.address,
            aggregates.items.c.hostname,
            aggregates.items.c.servicename
        )
        aggregates.add_join((Event, CorrEvent.idcause == Event.idevent))
        aggregates.add_contains_eager(CorrEvent.cause)
        aggregates.add_group_by(Event)
        aggregates.add_join((aggregates.items,
            Event.idsupitem == aggregates.items.c.idsupitem))
        aggregates.add_order_by(asc(aggregates.items.c.hostname))

        # On ne garde que les champs effectivement renseignés.
        for column in search.copy():
            if not search[column]:
                del search[column]

        # On sérialise les champs de type dict.
        def serialize_dict(dct, key):
            if isinstance(dct[key], dict):
                for subkey in dct[key]:
                    serialize_dict(dct[key], subkey)
                    dct['%s.%s' % (key, subkey)] = dct[key][subkey]
                del dct[key]
            elif isinstance(dct[key], datetime):
                dct[key] = dct[key].strftime(dateformat.get_date_format())
        fixed_search = search.copy()
        for column in fixed_search.copy():
            serialize_dict(fixed_search, column)

        # Pagination des résultats
        aggregates.generate_request()
        items_per_page = int(session.get('items_per_page', config['vigiboard_items_per_page']))
        page = paginate.Page(aggregates.req, page=page,
            items_per_page=items_per_page)

        # Récupération des données des plugins
        plugins_data = {}
        plugins = dict(config['columns_plugins'])

        ids_events = [event[0].idcause for event in page.items]
        ids_correvents = [event[0].idcorrevent for event in page.items]
        for plugin in plugins:
            plugin_data = plugins[plugin].get_bulk_data(ids_correvents)
            if plugin_data:
                plugins_data[plugin] = plugin_data
            else:
                plugins_data[plugin] = {}

        # Ajout des formulaires et préparation
        # des données pour ces formulaires.
        tmpl_context.last_modification = calendar.timegm(
            get_last_modification_timestamp(ids_events).timetuple())

        tmpl_context.edit_event_form = EditEventForm("edit_event_form",
            submit_text=_('Apply'), action=url('/update'))

        if request.response_type == 'text/csv':
            # Sans les 2 en-têtes suivants qui désactivent la mise en cache,
            # Internet Explorer refuse de télécharger le fichier CSV (cf. #961).
            response.headers['Pragma'] = 'public'           # Nécessaire pour IE.
            response.headers['Cache-Control'] = 'max-age=0' # Nécessaire pour IE.

            response.headers["Content-Type"] = "text/csv"
            response.headers['Content-Disposition'] = \
                            'attachment;filename="alerts.csv"'
            return export_csv.export(page, plugins_data)

        return dict(
            hostname = None,
            servicename = None,
            plugins_data = plugins_data,
            page = page,
            sort = sort,
            order = order,
            event_edit_status_options = edit_event_status_options,
            search_form = create_search_form,
            search = search,
            fixed_search = fixed_search,
        )


    class MaskedEventsSchema(schema.Schema):
        """Schéma de validation de la méthode masked_events."""
        idcorrevent = validators.Int(not_empty=True)
        page = validators.Int(min=1, if_missing=1, if_invalid=1)

    @validate(
        validators=MaskedEventsSchema(),
        error_handler = process_form_errors)
    @expose('raw_events_table.html')
    @require(access_restriction)
    def masked_events(self, idcorrevent, page=1):
        """
        Affichage de la liste des événements bruts masqués d'un événement
        corrélé (événements agrégés dans l'événement corrélé).

        @param page: numéro de la page à afficher.
        @type  page: C{int}
        @param idcorrevent: identifiant de l'événement corrélé souhaité.
        @type  idcorrevent: C{int}
        """

        # Auto-supervision
        self.get_failures()

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
                (CorrEvent, Event.idevent == CorrEvent.idcause),
            ).filter(CorrEvent.idcorrevent == idcorrevent
            ).one()

        if isinstance(cause_supitem, LowLevelService):
            hostname = cause_supitem.host.name
            servicename = cause_supitem.servicename
        elif isinstance(cause_supitem, Host):
            hostname = cause_supitem.name

        # Pagination des résultats
        events.generate_request()
        items_per_page = int(session.get('items_per_page', config['vigiboard_items_per_page']))
        page = paginate.Page(events.req, page=page,
            items_per_page=items_per_page)

        # Vérification que l'événement existe
        if not page.item_count:
            flash(_('No masked event or access denied'), 'error')
            redirect('/')

        return dict(
            idcorrevent = idcorrevent,
            hostname = hostname,
            servicename = servicename,
            plugins_data = {},
            page = page,
            search_form = create_search_form,
            search = {},
            fixed_search = {},
        )


    class EventSchema(schema.Schema):
        """Schéma de validation de la méthode event."""
        idevent = validators.Int(not_empty=True)
        page = validators.Int(min=1, if_missing=1, if_invalid=1)

    @validate(
        validators=EventSchema(),
        error_handler = process_form_errors)
    @expose('history_table.html')
    @require(access_restriction)
    def event(self, idevent, page=1):
        """
        Affichage de l'historique d'un événement brut.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param idevent: identifiant de l'événement brut souhaité.
        @type idevent: C{int}
        @param page: numéro de la page à afficher.
        @type page: C{int}

        Cette méthode permet de satisfaire l'exigence
        VIGILO_EXIG_VIGILO_BAC_0080.
        """

        # Auto-supervision
        self.get_failures()

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

        # Pagination des résultats
        items_per_page = int(session.get('items_per_page', config['vigiboard_items_per_page']))
        page = paginate.Page(history, page=page, items_per_page=items_per_page)
        event = events.req[0]

        return dict(
            idevent = idevent,
            hostname = event.hostname,
            servicename = event.servicename,
            plugins_data = {},
            page = page,
            search_form = create_search_form,
            search = {},
            fixed_search = {},
        )


    class ItemSchema(schema.Schema):
        """Schéma de validation de la méthode item."""
        # Si on ne passe pas le paramètre "page" ou qu'on passe une valeur
        # invalide ou pas de valeur du tout, alors on affiche la 1ère page.
        page = validators.Int(min=1, if_missing=1, if_invalid=1)

        # Paramètres de tri
        sort = validators.String(if_missing=None)
        order = validators.OneOf(['asc', 'desc'], if_missing='asc')

        # L'hôte / service dont on doit afficher les évènements
        host = validators.String(not_empty=True)
        service = validators.String(if_missing=None)

    @validate(
        validators=ItemSchema(),
        error_handler = process_form_errors)
    @expose('events_table.html')
    @require(access_restriction)
    def item(self, page=1, host=None, service=None, sort=None, order=None):
        """
        Affichage de l'historique de l'ensemble des événements corrélés
        jamais ouverts sur l'hôte / service demandé.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param page: Numéro de la page à afficher.
        @type: C{int}
        @param host: Nom de l'hôte souhaité.
        @type: C{str}
        @param service: Nom du service souhaité
        @type: C{str}
        @param sort: Colonne de tri
        @type: C{str} or C{None}
        @param order: Ordre du tri (asc ou desc)
        @type: C{str} or C{None}

        Cette méthode permet de satisfaire l'exigence
        VIGILO_EXIG_VIGILO_BAC_0080.
        """

        # Auto-supervision
        self.get_failures()

        idsupitem = SupItem.get_supitem(host, service)
        if not idsupitem:
            flash(_('No such host/service'), 'error')
            redirect('/')

        user = get_current_user()
        aggregates = VigiboardRequest(user, False, sort=sort, order=order)
        aggregates.add_table(
            CorrEvent,
            aggregates.items.c.hostname,
            aggregates.items.c.servicename,
        )
        aggregates.add_join((Event, CorrEvent.idcause == Event.idevent))
        aggregates.add_join((aggregates.items,
            Event.idsupitem == aggregates.items.c.idsupitem))
        aggregates.add_filter(aggregates.items.c.idsupitem == idsupitem)

        # Pagination des résultats
        aggregates.generate_request()
        items_per_page = int(session.get('items_per_page', config['vigiboard_items_per_page']))
        page = paginate.Page(aggregates.req, page=page,
            items_per_page=items_per_page)

        # Vérification qu'il y a au moins 1 événement qui correspond
        if not page.item_count:
            flash(_('No access to this host/service or no event yet'), 'error')
            redirect('/')

        # Ajout des formulaires et préparation
        # des données pour ces formulaires.
        ids_events = [event[0].idcause for event in page.items]
        tmpl_context.last_modification = calendar.timegm(
            get_last_modification_timestamp(ids_events).timetuple())

        tmpl_context.edit_event_form = EditEventForm("edit_event_form",
            submit_text=_('Apply'), action=url('/update'))

        plugins_data = {}
        for plugin in dict(config['columns_plugins']):
            plugins_data[plugin] = {}

        return dict(
            hostname = host,
            servicename = service,
            plugins_data = plugins_data,
            page = page,
            sort = sort,
            order = order,
            event_edit_status_options = edit_event_status_options,
            search_form = create_search_form,
            search = {},
            fixed_search = {},
        )


    class UpdateSchema(schema.Schema):
        """Schéma de validation de la méthode update."""
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
            Any(config.is_manager,
                has_permission('vigiboard-update'),
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

        # On récupère la liste de tous les identifiants des événements
        # à mettre à jour.
        ids = [ int(i) for i in id.strip(',').split(',') ]

        user = get_current_user()
        events = VigiboardRequest(user)
        events.add_table(
            CorrEvent,
            Event,
            events.items.c.hostname,
            events.items.c.servicename,
        )
        events.add_join((Event, CorrEvent.idcause == Event.idevent))
        events.add_join((events.items,
            Event.idsupitem == events.items.c.idsupitem))
        events.add_filter(CorrEvent.idcorrevent.in_(ids))

        events.generate_request()
        idevents = [event[0].idcause for event in events.req]

        # Si des changements sont survenus depuis que la
        # page est affichée, on en informe l'utilisateur.
        last_modification = datetime.utcfromtimestamp(last_modification)
        cur_last_modification = get_last_modification_timestamp(idevents, None)
        if cur_last_modification and last_modification < cur_last_modification:
            flash(_('Changes have occurred since the page was last displayed, '
                    'your changes HAVE NOT been saved.'), 'warning')
            raise redirect(request.environ.get('HTTP_REFERER', '/'))

        # Vérification que au moins un des identifiants existe et est éditable
        if not events.num_rows():
            flash(_('No access to this event'), 'error')
            redirect('/')

        if ack == u'Forced':
            condition = Any(
                config.is_manager,
                has_permission('vigiboard-admin'),
                msg=l_("You don't have administrative access "
                        "to VigiBoard"))
            try:
                condition.check_authorization(request.environ)
            except NotAuthorizedError as e:
                reason = unicode(e)
                flash(reason, 'error')
                raise redirect(request.environ.get('HTTP_REFERER', '/'))

        # Si un module de gestion de ticket est utilisé,
        # il a la possibilité de changer à la volée le libellé du ticket.
        if self._tickets:
            trouble_ticket = self._tickets.createTicket(events.req, trouble_ticket)

        # Définit 2 mappings dont les ensembles sont disjoincts
        # pour basculer entre la représentation en base de données
        # et la représentation "humaine" du bac à événements.
        ack_mapping = {
            # Permet d'associer la valeur dans le widget ToscaWidgets
            # (cf. vigiboard.widgets.edit_event.edit_event_status_options)
            # avec la valeur dans la base de données.
            u'None': CorrEvent.ACK_NONE,
            u'Acknowledged': CorrEvent.ACK_KNOWN,
            u'AAClosed': CorrEvent.ACK_CLOSED,

            # Permet d'afficher un libellé plus sympathique pour l'utilisateur
            # représentant l'état d'acquittement stocké en base de données.
            CorrEvent.ACK_NONE: l_('None'),
            CorrEvent.ACK_KNOWN: l_('Acknowledged'),
            CorrEvent.ACK_CLOSED: l_('Acknowledged and closed'),
        }

        # Modification des événements et création d'un historique
        # chaque fois que cela est nécessaire.
        for data in events.req:
            event = data[0]
            if trouble_ticket and trouble_ticket != event.trouble_ticket:
                history = EventHistory(
                        type_action=u"Ticket change",
                        idevent=event.idcause,
                        value=unicode(trouble_ticket),
                        text="Changed trouble ticket from '%(from)s' "
                             "to '%(to)s'" % {
                            'from': event.trouble_ticket,
                            'to': trouble_ticket,
                        },
                        username=user.user_name,
                        timestamp=datetime.utcnow(),
                    )
                DBSession.add(history)
                LOGGER.info(_('User "%(user)s" (%(address)s) changed the '
                            'trouble ticket from "%(previous)s" to "%(new)s" '
                            'on event #%(idevent)d') % {
                                'user': request.identity['repoze.who.userid'],
                                'address': request.remote_addr,
                                'previous': event.trouble_ticket,
                                'new': trouble_ticket,
                                'idevent': event.idcause,
                            })
                event.trouble_ticket = trouble_ticket

            # Changement du statut d'acquittement.
            if ack != u'NoChange':
                changed_ack = ack
                # Pour forcer l'acquittement d'un événement,
                # il faut en plus avoir la permission
                # "vigiboard-admin".
                if ack == u'Forced':
                    changed_ack = u'AAClosed'
                    cause = event.cause
                    # On met systématiquement l'événement à l'état "OK",
                    # même s'il s'agit d'un hôte.
                    # Techniquement, c'est incorrect, mais on fait ça
                    # pour masquer l'événement de toutes façons...
                    cause.current_state = \
                        StateName.statename_to_value(u'OK')

                    # Mise à jour de l'état dans State, pour que
                    # VigiMap soit également mis à jour.
                    DBSession.query(State).filter(
                            State.idsupitem == cause.idsupitem,
                        ).update({
                            'state': StateName.statename_to_value(u'OK'),
                        })

                    history = EventHistory(
                            type_action=u"Forced change state",
                            idevent=event.idcause,
                            value=u'OK',
                            text="Forced state to 'OK'",
                            username=user.user_name,
                            timestamp=datetime.utcnow(),
                            state=StateName.statename_to_value(u'OK'),
                        )
                    DBSession.add(history)
                    LOGGER.info(_('User "%(user)s" (%(address)s) forcefully '
                                'closed event #%(idevent)d') % {
                                    'user': request. \
                                            identity['repoze.who.userid'],
                                    'address': request.remote_addr,
                                    'idevent': event.idcause,
                                })

                # Convertit la valeur du widget ToscaWidgets
                # vers le code interne puis vers un libellé
                # "humain".
                ack_label = ack_mapping[ack_mapping[changed_ack]]

                # Si le changement a été forcé,
                # on veut le mettre en évidence.
                if ack == u'Forced':
                    history_label = u'Forced'
                else:
                    history_label = ack_label

                history = EventHistory(
                        type_action=u"Acknowledgement change state",
                        idevent=event.idcause,
                        value=unicode(history_label),
                        text=u"Changed acknowledgement status "
                            u"from '%s' to '%s'" % (
                            ack_mapping[event.ack],
                            ack_label,
                        ),
                        username=user.user_name,
                        timestamp=datetime.utcnow(),
                    )
                DBSession.add(history)
                LOGGER.info(_('User "%(user)s" (%(address)s) changed the state '
                            'from "%(previous)s" to "%(new)s" on event '
                            '#%(idevent)d') % {
                                'user': request.identity['repoze.who.userid'],
                                'address': request.remote_addr,
                                'previous': _(ack_mapping[event.ack]),
                                'new': _(ack_label),
                                'idevent': event.idcause,
                            })
                event.ack = ack_mapping[changed_ack]

        DBSession.flush()
        flash(_('Updated successfully'))
        redirect(request.environ.get('HTTP_REFERER', '/'))


    class GetPluginValueSchema(schema.Schema):
        """Schéma de validation de la méthode get_plugin_value."""
        idcorrevent = validators.Int(not_empty=True)
        plugin_name = validators.String(not_empty=True)
        # Permet de passer des paramètres supplémentaires au plugin.
        allow_extra_fields = True

    @validate(
        validators=GetPluginValueSchema(),
        error_handler = handle_validation_errors_json)
    @expose('json')
    @require(access_restriction)
    def plugin_json(self, idcorrevent, plugin_name, *arg, **krgv):
        """
        Permet de récupérer la valeur d'un plugin associée à un CorrEvent
        donné via JSON.
        """

        # Vérification de l'existence du plugin
        plugins = dict(config['columns_plugins'])
        if plugin_name not in plugins:
            raise HTTPNotFound(_("No such plugin '%s'") % plugin_name)

        # Récupération de la liste des évènements corrélés
        events = DBSession.query(CorrEvent.idcorrevent)

        # Filtrage des évènements en fonction des permissions de
        # l'utilisateur (s'il n'appartient pas au groupe 'managers')
        if not config.is_manager.is_met(request.environ):
            user = get_current_user()

            events = events.join(
                (Event, Event.idevent == CorrEvent.idcause),
            ).outerjoin(
                (LowLevelService, LowLevelService.idservice == Event.idsupitem),
            ).join(
                (SUPITEM_GROUP_TABLE,
                    or_(
                        SUPITEM_GROUP_TABLE.c.idsupitem == \
                            LowLevelService.idhost,
                        SUPITEM_GROUP_TABLE.c.idsupitem == \
                            Event.idsupitem,
                    )
                ),
            ).join(
                (GroupHierarchy,
                    GroupHierarchy.idchild == SUPITEM_GROUP_TABLE.c.idgroup),
            ).join(
                (DataPermission,
                    DataPermission.idgroup == GroupHierarchy.idparent),
            ).join(
                (USER_GROUP_TABLE,
                    USER_GROUP_TABLE.c.idgroup == DataPermission.idusergroup),
            ).filter(USER_GROUP_TABLE.c.username == user.user_name)

        # Filtrage des évènements en fonction
        # de l'identifiant passé en paramètre
        events = events.filter(CorrEvent.idcorrevent == idcorrevent).count()

        # Pas d'événement ou permission refusée. On ne distingue pas
        # les 2 cas afin d'éviter la divulgation d'informations.
        if events == 0:
            raise HTTPNotFound(_('No such incident or insufficient '
                                'permissions'))

        # L'évènement existe bien, et l'utilisateur dispose
        # des permissions appropriées. On fait alors appel au
        # plugin pour récupérer les informations à retourner.
        return plugins[plugin_name].get_json_data(idcorrevent, *arg, **krgv)

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
        session['refresh'] = bool(refresh)
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

    @validate(validators={"items": validators.Int()},
            error_handler = handle_validation_errors_json)
    @expose('json')
    def set_items_per_page(self, items):
        """Enregistre le nombre d'alertes par page dans les préférences."""
        session['items_per_page'] = items
        session.save()
        return dict()

    @require(access_restriction)
    @expose('json')
    def get_groups(self, parent_id=None, onlytype="", offset=0, noCache=None):
        """
        Affiche un étage de l'arbre de
        sélection des hôtes et groupes d'hôtes.

        @param parent_id: identifiant du groupe d'hôte parent
        @type  parent_id: C{int} or None
        """

        # Si l'identifiant du groupe parent n'est pas
        # spécifié, on retourne la liste des groupes
        # racines, fournie par la méthode get_root_groups.
        if parent_id is None:
            return self.get_root_groups()

        # TODO: Utiliser un schéma de validation
        parent_id = int(parent_id)
        offset = int(offset)

        # On récupère la liste des groupes de supitems dont
        # l'identifiant du parent est passé en paramètre.
        supitem_groups = DBSession.query(
                SupItemGroup.idgroup,
                SupItemGroup.name,
            ).join(
                (GroupHierarchy,
                    GroupHierarchy.idchild == SupItemGroup.idgroup),
            ).filter(GroupHierarchy.idparent == parent_id
            ).filter(GroupHierarchy.hops == 1
            ).order_by(SupItemGroup.name)

        # Si l'utilisateur n'appartient pas au groupe 'managers',
        # on filtre les résultats en fonction de ses permissions.
        if not config.is_manager.is_met(request.environ):
            user = get_current_user()
            GroupHierarchy_aliased = aliased(GroupHierarchy,
                name='GroupHierarchy_aliased')
            supitem_groups = supitem_groups.join(
                (GroupHierarchy_aliased,
                    or_(
                        GroupHierarchy_aliased.idchild == SupItemGroup.idgroup,
                        GroupHierarchy_aliased.idparent == SupItemGroup.idgroup
                    )),
                (DataPermission,
                    or_(
                        DataPermission.idgroup == \
                            GroupHierarchy_aliased.idparent,
                        DataPermission.idgroup == \
                            GroupHierarchy_aliased.idchild,
                    )),
                (USER_GROUP_TABLE, USER_GROUP_TABLE.c.idgroup == \
                    DataPermission.idusergroup),
            ).filter(USER_GROUP_TABLE.c.username == user.user_name)

        limit = int(config.get("max_menu_entries", 20))
        result = {"groups": [], "items": []}
        num_children_left = supitem_groups.distinct().count() - offset
        if offset:
            result["continued_from"] = offset
            result["continued_type"] = "group"
        all_grs = supitem_groups.distinct().limit(limit).offset(offset).all()
        for group in all_grs:
            result["groups"].append({
                'id'   : group.idgroup,
                'name' : group.name,
                'type' : "group",
            })
        if num_children_left > limit:
            result["groups"].append({
                'name': _("Next %(limit)s") % {"limit": limit},
                'offset': offset + limit,
                'parent_id': parent_id,
                'type': 'continued',
                'for_type': 'group',
            })

        return result

    def get_root_groups(self):
        """
        Retourne tous les groupes racines (c'est à dire n'ayant
        aucun parent) d'hôtes auquel l'utilisateur a accès.

        @return: Un dictionnaire contenant la liste de ces groupes.
        @rtype : C{dict} of C{list} of C{dict} of C{mixed}
        """

        # On récupère tous les groupes qui ont un parent.
        children = DBSession.query(
            SupItemGroup,
        ).distinct(
        ).join(
            (GroupHierarchy, GroupHierarchy.idchild == SupItemGroup.idgroup)
        ).filter(GroupHierarchy.hops > 0)

        # Ensuite on les exclut de la liste des groupes,
        # pour ne garder que ceux qui sont au sommet de
        # l'arbre et qui constituent nos "root groups".
        root_groups = DBSession.query(
            SupItemGroup,
        ).except_(children
        ).order_by(SupItemGroup.name)

        # On filtre ces groupes racines afin de ne
        # retourner que ceux auquels l'utilisateur a accès
        user = get_current_user()
        if not config.is_manager.is_met(request.environ):
            root_groups = root_groups.join(
                (GroupHierarchy,
                    GroupHierarchy.idparent == SupItemGroup.idgroup),
                (DataPermission,
                    DataPermission.idgroup == GroupHierarchy.idchild),
                (USER_GROUP_TABLE, USER_GROUP_TABLE.c.idgroup == \
                    DataPermission.idusergroup),
            ).filter(USER_GROUP_TABLE.c.username == user.user_name)

        groups = []
        for group in root_groups.all():
            groups.append({
                'id'   : group.idgroup,
                'name' : group.name,
                'type' : "group",
            })

        return dict(groups=groups, items=[])

def get_last_modification_timestamp(event_id_list,
                                    value_if_none=datetime.utcnow):
    """
    Récupère le timestamp de la dernière modification
    opérée sur l'un des événements dont l'identifiant
    fait partie de la liste passée en paramètre.
    """
    if not event_id_list:
        last_modification_timestamp = None
    else:
        last_modification_timestamp = DBSession.query(
                                func.max(EventHistory.timestamp),
                         ).filter(EventHistory.idevent.in_(event_id_list)
                         ).scalar()

    if not last_modification_timestamp:
        if not callable(value_if_none):
            return value_if_none
        else:
            last_modification_timestamp = value_if_none()
    return last_modification_timestamp

# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
################################################################################
#
# Copyright (C) 2007-2011 CS-SI
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
################################################################################

"""VigiBoard Controller"""

from datetime import datetime
from time import mktime

from pkg_resources import resource_filename

from tg.exceptions import HTTPNotFound
from tg import expose, validate, require, flash, url, \
    tmpl_context, request, config, session, redirect
from webhelpers import paginate
from tw.forms import validators
from pylons.i18n import ugettext as _, lazy_ugettext as l_, get_lang
from sqlalchemy import asc
from sqlalchemy.sql import func
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import or_
from repoze.what.predicates import Any, All, in_group, \
                                    has_permission, not_anonymous, \
                                    NotAuthorizedError
from formencode import schema

from vigilo.models.session import DBSession
from vigilo.models.tables import Event, EventHistory, CorrEvent, Host, \
                                    SupItem, SupItemGroup, LowLevelService, \
                                    StateName, State, DataPermission
from vigilo.models.tables.grouphierarchy import GroupHierarchy
from vigilo.models.tables.secondary_tables import EVENTSAGGREGATE_TABLE, \
        USER_GROUP_TABLE, SUPITEM_GROUP_TABLE

from vigilo.turbogears.controllers.autocomplete import AutoCompleteController
from vigilo.turbogears.controllers.proxy import ProxyController
from vigilo.turbogears.controllers.api.root import ApiRootController
from vigilo.turbogears.helpers import get_current_user

from vigiboard.controllers.vigiboardrequest import VigiboardRequest
from vigiboard.controllers.vigiboard_controller import VigiboardRootController
from vigiboard.controllers.feeds import FeedsController

from vigiboard.widgets.edit_event import edit_event_status_options, \
                                            EditEventForm
from vigiboard.widgets.search_form import create_search_form
import logging

LOGGER = logging.getLogger(__name__)

__all__ = ('RootController', 'get_last_modification_timestamp',
           'date_to_timestamp')

# pylint: disable-msg=R0201
class RootController(VigiboardRootController):
    """
    Le controller général de vigiboard
    """
    autocomplete = AutoCompleteController()
    nagios = ProxyController('nagios', '/nagios/',
        not_anonymous(l_('You need to be authenticated')))
    api = ApiRootController("/api")
    feeds = FeedsController()

    # Prédicat pour la restriction de l'accès aux interfaces.
    # L'utilisateur doit avoir la permission "vigiboard-access"
    # ou appartenir au groupe "managers" pour accéder à VigiBoard.
    access_restriction = All(
        not_anonymous(msg=l_("You need to be authenticated")),
        Any(in_group('managers'),
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

    class DefaultSchema(schema.Schema):
        """Schéma de validation de la méthode default."""
        page = validators.Int(min=1, if_missing=1, if_invalid=1)

        # Nécessaire pour que les critères de recherche soient conservés.
        allow_extra_fields = True

        # 2ème validation, cette fois avec les champs
        # du formulaire de recherche.
        chained_validators = [create_search_form.validator]

    @validate(
        validators=DefaultSchema(),
        error_handler = process_form_errors)
    @expose('events_table.html')
    @require(access_restriction)
    def default(self, page, **search):
        """
        Page d'accueil de Vigiboard. Elle affiche, suivant la page demandée
        (page 1 par defaut), la liste des événements, rangés par ordre de prise
        en compte, puis de sévérité.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param page: Numéro de la page souhaitée, commence à 1
        @type page: C{int}
        @param search: Dictionnaire contenant les critères de recherche.
        @type search: C{dict}

        Cette méthode permet de satisfaire les exigences suivantes :
            - VIGILO_EXIG_VIGILO_BAC_0040,
            - VIGILO_EXIG_VIGILO_BAC_0070,
            - VIGILO_EXIG_VIGILO_BAC_0100,
        """

        user = get_current_user()
        aggregates = VigiboardRequest(user, search=search)

        aggregates.add_table(
            CorrEvent,
            aggregates.items.c.hostname,
            aggregates.items.c.servicename
        )
        aggregates.add_join((Event, CorrEvent.idcause == Event.idevent))
        aggregates.add_contains_eager(CorrEvent.cause)
        aggregates.add_group_by(Event)
        aggregates.add_join((aggregates.items,
            Event.idsupitem == aggregates.items.c.idsupitem))
        aggregates.add_order_by(asc(aggregates.items.c.hostname))

        # Certains arguments sont réservés dans routes.util.url_for().
        # On effectue les substitutions adéquates.
        # Par exemple: "host" devient "host_".
        reserved = ('host', 'anchor', 'protocol', 'qualified')
        for column in search.copy():
            if column in reserved:
                search[column + '_'] = search[column]
                del search[column]

        # On ne garde que les champs effectivement renseignés.
        for column in search.copy():
            if not search[column]:
                del search[column]

        # On sérialise les champs de type dict.
        def serialize_dict(dct, key):
            if isinstance(dct[key], dict):
                for subkey in dct[key]:
                    serialize_dict(dct[key], subkey)
                    dct[key+'.'+subkey] = dct[key][subkey]
                del dct[key]
        fixed_search = search.copy()
        for column in fixed_search.copy():
            serialize_dict(fixed_search, column)

        # Pagination des résultats
        aggregates.generate_request()
        items_per_page = int(config['vigiboard_items_per_page'])
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

        # Ajout des formulaires et préparation
        # des données pour ces formulaires.
        tmpl_context.last_modification = \
            mktime(get_last_modification_timestamp(ids_events).timetuple())

        tmpl_context.edit_event_form = EditEventForm("edit_event_form",
            submit_text=_('Apply'), action=url('/update'))

        return dict(
            hostname = None,
            servicename = None,
            plugins_data = plugins_data,
            page = page,
            event_edit_status_options = edit_event_status_options,
            search_form = create_search_form,
            search = search,
            fixed_search = fixed_search,
        )


    @expose()
    def i18n(self):
        import gettext
        import pylons
        import os.path

        # Repris de pylons.i18n.translation:_get_translator.
        conf = pylons.config.current_conf()
        try:
            rootdir = conf['pylons.paths']['root']
        except KeyError:
            rootdir = conf['pylons.paths'].get('root_path')
        localedir = os.path.join(rootdir, 'i18n')

        lang = get_lang()

        # Localise le fichier *.mo actuellement chargé
        # et génère le chemin jusqu'au *.js correspondant.
        filename = gettext.find(conf['pylons.package'], localedir,
            languages=lang)
        js = filename[:-3] + '.js'

        themes_filename = gettext.find(
            'vigilo-themes',
            resource_filename('vigilo.themes.i18n', ''),
            languages=lang)
        themes_js = themes_filename[:-3] + '.js'

        # Récupère et envoie le contenu du fichier de traduction *.js.
        fhandle = open(js, 'r')
        translations = fhandle.read()
        fhandle.close()

        fhandle = open(themes_js, 'r')
        translations += fhandle.read()
        fhandle.close()
        return translations


    class MaskedEventsSchema(schema.Schema):
        """Schéma de validation de la méthode masked_events."""
        idcorrevent = validators.Int(not_empty=True)
        page = validators.Int(min=1, if_missing=1, if_invalid=1)

    @validate(
        validators=MaskedEventsSchema(),
        error_handler = process_form_errors)
    @expose('raw_events_table.html')
    @require(access_restriction)
    def masked_events(self, idcorrevent, page):
        """
        Affichage de la liste des événements bruts masqués d'un événement
        corrélé (événements agrégés dans l'événement corrélé).

        @param idcorrevent: identifiant de l'événement corrélé souhaité.
        @type idcorrevent: C{int}
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
        items_per_page = int(config['vigiboard_items_per_page'])
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
    def event(self, idevent, page):
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
        items_per_page = int(config['vigiboard_items_per_page'])
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

        @param page: Numéro de la page à afficher.
        @param host: Nom de l'hôte souhaité.
        @param service: Nom du service souhaité

        Cette méthode permet de satisfaire l'exigence
        VIGILO_EXIG_VIGILO_BAC_0080.
        """
        idsupitem = SupItem.get_supitem(host, service)
        if not idsupitem:
            flash(_('No such host/service'), 'error')
            redirect('/')

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

        # Pagination des résultats
        aggregates.generate_request()
        items_per_page = int(config['vigiboard_items_per_page'])
        page = paginate.Page(aggregates.req, page=page,
            items_per_page=items_per_page)

        # Vérification qu'il y a au moins 1 événement qui correspond
        if not page.item_count:
            flash(_('No access to this host/service or no event yet'), 'error')
            redirect('/')

        # Ajout des formulaires et préparation
        # des données pour ces formulaires.
        ids_events = [event[0].idcause for event in page.items]
        tmpl_context.last_modification = \
            mktime(get_last_modification_timestamp(ids_events).timetuple())

        tmpl_context.edit_event_form = EditEventForm("edit_event_form",
            submit_text=_('Apply'), action=url('/update'))

        return dict(
            hostname = host,
            servicename = service,
            plugins_data = {},
            page = page,
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
            Any(in_group('managers'),
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
        ids = map(int, id.strip(',').split(','))

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

        # Modification des événements et création d'un historique
        # chaque fois que cela est nécessaire.
        for event in events.req:
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
                        timestamp=datetime.now(),
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
                            timestamp=datetime.now(),
                        )
                    DBSession.add(history)
                    LOGGER.info(_('User "%(user)s" (%(address)s) forcefully '
                                'closed event #%(idevent)d') % {
                                    'user': request. \
                                            identity['repoze.who.userid'],
                                    'address': request.remote_addr,
                                    'idevent': event.idcause,
                                })
 
                history = EventHistory(
                        type_action=u"Acknowledgement change state",
                        idevent=event.idcause,
                        value=ack,
                        text="Changed acknowledgement status "
                            "from '%s' to '%s'" % (
                            event.status, changed_ack
                        ),
                        username=user.user_name,
                        timestamp=datetime.now(),
                    )
                DBSession.add(history)
                LOGGER.info(_('User "%(user)s" (%(address)s) changed the state '
                            'from "%(previous)s" to "%(new)s" on event '
                            '#%(idevent)d') % {
                                'user': request.identity['repoze.who.userid'],
                                'address': request.remote_addr,
                                'previous': event.status,
                                'new': changed_ack,
                                'idevent': event.idcause,
                            })
                event.status = changed_ack

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
        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:

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
        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:
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
        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:

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

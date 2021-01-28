# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Un plugin pour VigiBoard qui ajoute une colonne avec les liens vers les
entrées d'historiques liées à l'événement, ainsi que les liens vers les
applications externes.
"""

import urllib
from tg import config, url, request
from tg.i18n import lazy_ugettext as l_
import tw.forms as twf
from sqlalchemy.sql.expression import null as expr_null, union_all
from sqlalchemy import func

from tg.predicates import has_permission, in_group
from vigilo.turbogears.helpers import get_current_user

from vigilo.models.session import DBSession
from vigilo.models.tables import Event, CorrEvent, Host, LowLevelService, \
    StateName, Map, MapNode, MapNodeHost, MapGroup
from vigilo.models.tables.secondary_tables import MAP_GROUP_TABLE

from vigiboard.controllers.plugins import VigiboardRequestPlugin, ITEMS


class PluginDetails(VigiboardRequestPlugin):
    """
    Plugin qui ajoute des liens vers les historiques et les applications
    externes.
    """

    def get_json_data(self, idcorrevent, *args, **kwargs):
        """
        Renvoie les éléments pour l'affichage de la fenêtre de dialogue
        contenant des détails sur un événement corrélé.

        @param idcorrevent: identifiant de l'événement corrélé.
        @type idcorrevent: C{int}
        """

        # Obtention de données sur l'événement et sur son historique
        host_query = DBSession.query(
            Host.idhost.label("idsupitem"),
            Host.idhost.label("idhost"),
            Host.name.label("host"),
            expr_null().label("service"),
        )
        lls_query = DBSession.query(
            LowLevelService.idservice.label("idsupitem"),
            Host.idhost.label("idhost"),
            Host.name.label("host"),
            LowLevelService.servicename.label("service"),
        ).join(
            (Host, Host.idhost == LowLevelService.idhost),
        )
        supitems = union_all(lls_query, host_query, correlate=False).alias()
        event = DBSession.query(
            CorrEvent.idcorrevent,
            CorrEvent.idcause,
            supitems.c.idhost,
            supitems.c.host,
            supitems.c.service,
            Event.message,
            Event.initial_state,
            Event.current_state,
            Event.peak_state
        ).join(
            (Event, Event.idevent == CorrEvent.idcause),
            (supitems, supitems.c.idsupitem == Event.idsupitem),
        ).filter(CorrEvent.idcorrevent == idcorrevent
        ).first()

        # On détermine les cartes auxquelles cet utilisateur a accès.
        user_maps = []
        max_maps = int(config['max_maps'])
        is_manager = config.is_manager.is_met(request.environ)
        if max_maps != 0 and (is_manager or
            has_permission('vigimap-access').is_met(request.environ)):
            items = DBSession.query(
                    Map.idmap,
                    Map.title,
                ).distinct(
                ).join(
                    (MAP_GROUP_TABLE, MAP_GROUP_TABLE.c.idmap == Map.idmap),
                    (MapNodeHost, MapNodeHost.idmap == Map.idmap),
                ).order_by(func.lower(Map.title).asc()
                ).filter(MapNodeHost.idhost == event.idhost)

            if not is_manager:
                mapgroups = get_current_user().mapgroups(only_direct=True)
                # pylint: disable-msg=E1103
                items = items.filter(MAP_GROUP_TABLE.c.idgroup.in_(mapgroups))

            # La valeur -1 supprime la limite.
            if max_maps > 0:
                # On limite au nombre maximum de cartes demandés + 1.
                # Un message sera affiché s'il y a effectivement plus
                # de cartes que la limite configurée.
                items = items.limit(max_maps + 1)

            user_maps = [(m.idmap, m.title) for m in items.all()]

        context = {
            'idcorrevent': idcorrevent,
            'host': event.host,
            'service': event.service,
            'message': event.message,
            'maps': user_maps,
            'current_state': StateName.value_to_statename(event.current_state),
            'initial_state': StateName.value_to_statename(event.initial_state),
            'peak_state': StateName.value_to_statename(event.peak_state),
        }

        eventdetails = {}
        for edname, edlink in enumerate(config['vigiboard_links.eventdetails']):
            # Évite que les gardes ne se polluent entre elles.
            local_ctx = context.copy()

            # Les liens peuvent être conditionnés à l'aide
            # d'une expression ou d'un callable qui agira
            # comme un prédicat de test.
            if 'only_if' in edlink:
                if callable(edlink['only_if']):
                    display_link = edlink['only_if'](local_ctx)
                else:
                    display_link = edlink['only_if']
                if not display_link:
                    continue

            if callable(edlink['uri']):
                uri = edlink['uri'](local_ctx)
            else:
                uri = edlink['uri'] % local_ctx

            eventdetails[unicode(edname)] = {
                'url': url(uri),
                'target': edlink.get('target', '_blank')
            }

        return dict(
                current_state = StateName.value_to_statename(
                                    event.current_state),
                initial_state = StateName.value_to_statename(
                                    event.initial_state),
                peak_state = StateName.value_to_statename(
                                    event.peak_state),
                idcorrevent = idcorrevent,
                host = event.host,
                service = event.service,
                eventdetails = eventdetails,
                maps = user_maps,
                idcause = event.idcause,
            )

    def get_data(self, event):
        state = StateName.value_to_statename(event[0].cause.current_state)
        peak_state = StateName.value_to_statename(event[0].cause.peak_state)
        init_state = StateName.value_to_statename(event[0].cause.initial_state)
        return {
            'state': state,
            'peak_state': peak_state,
            'initial_state': init_state,
            'id': event[0].idcorrevent,
        }

    def get_search_fields(self):
        states = DBSession.query(StateName.idstatename, StateName.statename
                    ).order_by(StateName.order.asc()).all()
        # Liste des valeurs acceptées pour la validation.
        valid = []
        # Liste des options présentes dans le champ de sélection.
        options = []
        for s in states:
            valid.extend([str(s.idstatename), s.statename])
            options.append( (
                str(s.idstatename),
                s.statename,
                {'title': l_(s.statename)}
            ) )

        return [
            twf.MultipleSelectField(
                'state',
                label_text=l_('Current state'),
                options=options,
                validator=twf.validators.OneOf(
                    valid,
                    if_invalid=[],
                    if_missing=[],
                ),
            ),
        ]

    def handle_search_fields(self, query, search, state, subqueries):
        if state != ITEMS:
            return

        states = []
        for value in search.get('state', []):
            try:
                states.append(int(value))
            except (ValueError, TypeError):
                try:
                    states.append(StateName.statename_to_value(value))
                except:
                    # On ignore silencieusement un critère de recherche erroné
                    pass

        if states:
            query.add_filter(Event.current_state.in_(states))

    def get_sort_criterion(self, query, column):
        columns = {
            'details': StateName.order,
            'problem': StateName.statename.in_([u'OK', u'UP']),
        }
        return columns.get(column)


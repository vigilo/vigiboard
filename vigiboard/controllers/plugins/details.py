# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
################################################################################
#
# Copyright (C) 2007-2015 CS-SI
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

"""
Un plugin pour VigiBoard qui ajoute une colonne avec les liens vers les
entrées d'historiques liées à l'événement, ainsi que les liens vers les
applications externes.
"""

import urllib
from tg import config, url, request
from pylons.i18n import lazy_ugettext as l_
import tw.forms as twf
from sqlalchemy.sql.expression import null as expr_null, union_all
from sqlalchemy import func

from repoze.what.predicates import has_permission, in_group
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
                    func.lower(Map.title),
                ).distinct(
                ).join(
                    (MAP_GROUP_TABLE, MAP_GROUP_TABLE.c.idmap == Map.idmap),
                    (MapGroup, MapGroup.idgroup == MAP_GROUP_TABLE.c.idgroup),
                    (MapNodeHost, MapNodeHost.idmap == Map.idmap),
                ).order_by(func.lower(Map.title).asc()
                ).filter(MapNodeHost.idhost == event.idhost)

            if not is_manager:
                mapgroups = get_current_user().mapgroups(only_direct=True)
                # pylint: disable-msg=E1103
                items = items.filter(MapGroup.idgroup.in_(mapgroups))

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
        options = [('', u'')] + \
                    [( str(s.idstatename), s.statename ) for s in states]
        return [
            twf.SingleSelectField(
                'state',
                label_text=l_('Current state'),
                options=options,
                validator=twf.validators.OneOf(
                    dict(options).keys(),
                    if_invalid=None,
                    if_missing=None,
                ),
            ),
        ]

    def handle_search_fields(self, query, search, state, subqueries):
        if state != ITEMS:
            return

        if search.get('state'):
            try:
                query.add_filter(Event.current_state == int(search['state']))
            except (ValueError, TypeError):
                # On ignore silencieusement le critère de recherche erroné.
                pass

    def get_sort_criterion(self, query, column):
        if column == 'details':
            return StateName.order
        return None


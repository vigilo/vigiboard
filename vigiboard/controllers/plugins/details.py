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

"""
Un plugin pour VigiBoard qui ajoute une colonne avec les liens vers les
entrées d'historiques liées à l'événement, ainsi que les liens vers les
applications externes.
"""

from tg import config, url
from sqlalchemy.sql.expression import null as expr_null, union_all

from vigilo.models.session import DBSession
from vigilo.models.tables import Event, \
    CorrEvent, Host, LowLevelService, StateName

from vigiboard.controllers.plugins import VigiboardRequestPlugin

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
            Host.name.label("host"),
            expr_null().label("service"),
        )
        lls_query = DBSession.query(
            LowLevelService.idservice.label("idsupitem"),
            Host.name.label("host"),
            LowLevelService.servicename.label("service"),
        ).join(
            (Host, Host.idhost == LowLevelService.idhost),
        )
        supitems = union_all(lls_query, host_query, correlate=False).alias()
        event = DBSession.query(
            CorrEvent.idcorrevent,
            CorrEvent.idcause,
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

        context = {
            'idcorrevent': idcorrevent,
            'host': event.host,
            'service': event.service,
            'message': event.message,
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
                idcause = event.idcause,
            )

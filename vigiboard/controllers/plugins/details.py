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

import urllib

from tg.exceptions import HTTPForbidden
from tg import config, url

from sqlalchemy.sql.expression import null as expr_null, union_all
from vigilo.models.session import DBSession
from vigilo.models.tables import Event, \
    CorrEvent, Host, LowLevelService, StateName

from vigiboard.controllers.plugins import VigiboardRequestPlugin
from vigilo.turbogears.helpers import get_current_user

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

        eventdetails = {}
        for edname, edlink in enumerate(config['vigiboard_links.eventdetails']):

            if event.service:
                service = urllib.quote(event.service)
            else:
                service = None

            eventdetails[unicode(edname)] = url(edlink[1]) % {
                'idcorrevent': idcorrevent,
                'host': urllib.quote(event.host),
                'service': service,
                'message': urllib.quote(event.message.encode('utf-8')),
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

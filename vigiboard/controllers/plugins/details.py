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

from vigiboard.controllers.vigiboardrequest import VigiboardRequest
from vigiboard.controllers.plugins import VigiboardRequestPlugin
from vigilo.models.tables import CorrEvent, Event, StateName
from vigilo.turbogears.helpers import get_current_user

class PluginDetails(VigiboardRequestPlugin):
    """
    Plugin qui ajoute des liens vers les historiques et les applications
    externes.
    """

    def get_value(self, idcorrevent, *args, **kwargs):
        """
        Renvoie les éléments pour l'affichage de la fenêtre de dialogue
        contenant des détails sur un événement corrélé.

        @param idcorrevent: identifiant de l'événement corrélé.
        @type idcorrevent: C{int}
        """

        # Obtention de données sur l'événement et sur son historique
        user = get_current_user()
        if user is None:
            return None

        events = VigiboardRequest(user, False)
        events.add_table(
            Event,
            events.items.c.hostname,
            events.items.c.servicename,
        )
        events.add_join((CorrEvent, CorrEvent.idcause == Event.idevent))
        events.add_join((events.items,
            Event.idsupitem == events.items.c.idsupitem))
        events.add_filter(CorrEvent.idcorrevent == idcorrevent)

        # Vérification que au moins un des identifiants existe et est éditable
        if events.num_rows() != 1:
            raise HTTPForbidden()

        event = events.req[0]
        eventdetails = {}
        for edname, edlink in enumerate(config['vigiboard_links.eventdetails']):

            if event.servicename:
                service = urllib.quote(event.servicename)
            else:
                service = None

            eventdetails[unicode(edname)] = url(edlink[1]) % {
                'idcorrevent': idcorrevent,
                'host': urllib.quote(event.hostname),
                'service': service,
                'message': urllib.quote(event[0].message),
            }

        return dict(
                current_state = StateName.value_to_statename(
                                    event[0].current_state),
                initial_state = StateName.value_to_statename(
                                    event[0].initial_state),
                peak_state = StateName.value_to_statename(
                                    event[0].peak_state),
                idcorrevent = idcorrevent,
                host = event.hostname,
                service = event.servicename,
                eventdetails = eventdetails,
                idcause = event[0].idevent,
            )

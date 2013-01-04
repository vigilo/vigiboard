# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
################################################################################
#
# Copyright (C) 2007-2013 CS-SI
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
Un plugin pour VigiBoard qui ajoute une colonne avec le nombre
d'événements masqués d'un événement corrélé.
"""
from sqlalchemy.sql import functions as func
from vigiboard.controllers.plugins import VigiboardRequestPlugin

from vigilo.models.session import DBSession
from vigilo.models.tables.secondary_tables import EVENTSAGGREGATE_TABLE

class PluginMaskedEvents(VigiboardRequestPlugin):
    """
    Affiche le nombre d'événements masqués par l'événement corrélé.
    """
    def get_bulk_data(self, events_ids):
        """
        Renvoie le nombre d'événements masqués par celui-ci.

        @param events_ids: Liste des identifiants des événements corrélés
            à afficher.
        @type events_ids: C{int}
        @return: Un dictionnaire associant à chaque identifiant d'évènement
            le nombre d'événements masqués.
        @rtype: C{dict}
        """
        counts = DBSession.query(
                func.count().label('masked'),
                EVENTSAGGREGATE_TABLE.c.idcorrevent
            ).group_by(EVENTSAGGREGATE_TABLE.c.idcorrevent
            ).filter(EVENTSAGGREGATE_TABLE.c.idcorrevent.in_(events_ids))

        res = {}
        for count in counts:
            # Il faut retirer la cause du décompte.
            res[count.idcorrevent] = count.masked - 1
        return res

    def get_data(self, event):
        return {
            'id': event[0].idcorrevent,
        }

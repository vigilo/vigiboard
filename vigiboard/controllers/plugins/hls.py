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
Un plugin pour VigiBoard qui ajoute une colonne avec les services de haut
niveau (L{HighLevelService}) impactés par un événement.
"""

from vigiboard.controllers.plugins import VigiboardRequestPlugin
from vigilo.models.session import DBSession
from vigilo.models.tables import HighLevelService, CorrEvent, Event, SupItem

class PluginHLS(VigiboardRequestPlugin):
    """
    Plugin qui permet de voir les services de haut niveau impactés par
    un événement.
    """
    def get_value(self, idcorrevent):
        """
        Renvoie le nom des services de haut niveau impactés par l'événement.

        @param idcorrevent: Identifiant de l'événement corrélé.
        @type idcorrevent: C{int}
        @return: Un dictionnaire dont la clé "services" contient une liste
            des noms des services de haut niveau impactés par l'événement
            corrélé dont l'identifiant est L{idcorrevent}.
        """
        supitem = self.get_correvent_supitem(idcorrevent)

        if not supitem:
            return []

        services = supitem.impacted_hls(
            HighLevelService.servicename
        ).distinct().order_by(
            HighLevelService.servicename.asc()
        ).all()

        return {'services': [service.servicename for service in services]}

    def get_correvent_supitem(self, idcorrevent):
        """
        Retourne le supitem ayant causé l'évènement
        corrélé dont l'identifiant est passé en paramètre.
        """
        # On récupère l'item recherché dans la BDD
        supitem = DBSession.query(SupItem
            ).join(
                (Event, Event.idsupitem == SupItem.idsupitem),
                (CorrEvent, CorrEvent.idcause == Event.idevent),
            ).filter(CorrEvent.idcorrevent == idcorrevent).first()
        return supitem

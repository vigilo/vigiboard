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
from vigilo.models.tables import HighLevelService, CorrEvent, Event, SupItem, \
    ImpactedHLS, ImpactedPath
from sqlalchemy.orm import aliased
from sqlalchemy.sql import functions

class PluginHLS(VigiboardRequestPlugin):
    """
    Plugin qui permet de voir les services de haut niveau impactés par
    les événements affichés sur la page principale de VigiBoard.
    """

    def get_bulk_data(self, events_ids):
        """
        Renvoie le nom des services de haut niveau impactés
        par chacun des événements du tableau de VigiBoard.

        @param events_ids: Liste des identifiants des événements corrélés
            à afficher.
        @type  events_ids: C{int}
        @return: Un dictionnaire associant à chaque identifiant d'évènement
            la liste des noms des HLS de plus haut niveau qu'il impacte.
        @rtype:  C{dict}
        """

        imp_hls1 = aliased(ImpactedHLS)
        imp_hls2 = aliased(ImpactedHLS)

        # Sous-requête récupérant les identifiants des supitems
        # impactés par les évènements passés en paramètre.
        subquery = DBSession.query(
                SupItem.idsupitem,
                CorrEvent.idcorrevent
            ).join(
                (Event, Event.idsupitem == SupItem.idsupitem),
                (CorrEvent, CorrEvent.idcause == Event.idevent),
            ).filter(CorrEvent.idcorrevent.in_(events_ids)
            ).subquery()

        # Sous-requête récupérant les identifiants des SHN de plus
        # haut niveau impactés par les évènements passés en paramètre.
        # Fait appel à la sous-requête précédente (subquery).
        subquery2 = DBSession.query(
            functions.max(imp_hls1.distance).label('distance'),
            imp_hls1.idpath,
            subquery.c.idcorrevent
        ).join(
            (ImpactedPath, ImpactedPath.idpath == imp_hls1.idpath)
        ).join(
            (subquery, ImpactedPath.idsupitem == subquery.c.idsupitem)
        ).group_by(imp_hls1.idpath, subquery.c.idcorrevent
        ).subquery()

        # Requête récupérant les noms des SHN de plus haut niveau
        # impactés par chacun des évènements passés en paramètre.
        # Fait appel à la sous-requête précédente (subquery2).
        services = DBSession.query(
            HighLevelService.servicename,
            subquery2.c.idcorrevent
        ).distinct(
        ).join(
            (imp_hls2, HighLevelService.idservice == imp_hls2.idhls),
            (subquery2, subquery2.c.idpath == imp_hls2.idpath),
        ).filter(imp_hls2.distance == subquery2.c.distance
        ).order_by(
            HighLevelService.servicename.asc()
        ).all()

        # Construction d'un dictionnaire associant à chaque évènement
        # le nom des SHN de plus haut niveau qu'il impacte.
        hls = {}
        for event_id in events_ids:
            hls[event_id] = []
        for service in services:
            hls[service.idcorrevent].append(service.servicename)

        return hls


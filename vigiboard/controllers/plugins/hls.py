# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2016 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Un plugin pour VigiBoard qui ajoute une colonne avec les services de haut
niveau (L{HighLevelService}) impactés par un événement.
"""

import tw.forms as twf
from pylons.i18n import lazy_ugettext as l_

from vigiboard.controllers.plugins import VigiboardRequestPlugin, INNER
from vigilo.models.session import DBSession
from vigilo.models.functions import sql_escape_like
from vigilo.models import tables
from sqlalchemy.orm import aliased
from sqlalchemy.sql import functions

class PluginHLS(VigiboardRequestPlugin):
    """
    Plugin qui permet de voir les services de haut niveau impactés par
    les événements affichés sur la page principale de VigiBoard.
    """
    def get_search_fields(self):
        return [
            twf.TextField(
                'hls',
                label_text=l_('High-Level Service'),
                validator=twf.validators.String(if_missing=None),
            )
        ]

    def handle_search_fields(self, query, search, state, subqueries):
        if state != INNER or not search.get('hls'):
            return
        hls = sql_escape_like(search['hls'])

        # Il s'agit d'un manager. On applique le filtre
        # indépendamment aux 2 sous-requêtes.
        if len(subqueries) == 2:
            subqueries[0] = subqueries[0].join(
                    (tables.ImpactedPath, tables.ImpactedPath.idsupitem == \
                        tables.LowLevelService.idservice),
                    (tables.ImpactedHLS, tables.ImpactedHLS.idpath == \
                        tables.ImpactedPath.idpath),
                    (tables.HighLevelService, \
                        tables.HighLevelService.idservice == \
                        tables.ImpactedHLS.idhls),
                ).filter(tables.HighLevelService.servicename.ilike(hls))

            subqueries[1] = subqueries[1].join(
                    (tables.ImpactedPath, tables.ImpactedPath.idsupitem == \
                        tables.Host.idhost),
                    (tables.ImpactedHLS, tables.ImpactedHLS.idpath == \
                        tables.ImpactedPath.idpath),
                    (tables.HighLevelService,
                        tables.HighLevelService.idservice == \
                        tables.ImpactedHLS.idhls),
                ).filter(tables.HighLevelService.servicename.ilike(hls))

        # Il s'agit d'un utilisateur normal.
        else:
            subqueries[0] = subqueries[0].join(
                    (tables.ImpactedPath, tables.ImpactedPath.idsupitem == \
                        tables.UserSupItem.idsupitem),
                    (tables.ImpactedHLS, tables.ImpactedHLS.idpath == \
                        tables.ImpactedPath.idpath),
                    (tables.HighLevelService,
                        tables.HighLevelService.idservice == \
                        tables.ImpactedHLS.idhls),
                ).filter(tables.HighLevelService.servicename.ilike(hls))

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

        if not events_ids:
            return {}

        imp_hls1 = aliased(tables.ImpactedHLS)
        imp_hls2 = aliased(tables.ImpactedHLS)

        # Sous-requête récupérant les identifiants des supitems
        # impactés par les évènements passés en paramètre.
        subquery = DBSession.query(
                tables.SupItem.idsupitem,
                tables.CorrEvent.idcorrevent
            ).join(
                (tables.Event, tables.Event.idsupitem == \
                    tables.SupItem.idsupitem),
                (tables.CorrEvent, tables.CorrEvent.idcause == \
                    tables.Event.idevent),
            ).filter(tables.CorrEvent.idcorrevent.in_(events_ids)
            ).subquery()

        # Sous-requête récupérant les identifiants des SHN de plus
        # haut niveau impactés par les évènements passés en paramètre.
        # Fait appel à la sous-requête précédente (subquery).
        subquery2 = DBSession.query(
            functions.max(imp_hls1.distance).label('distance'),
            imp_hls1.idpath,
            subquery.c.idcorrevent
        ).join(
            (tables.ImpactedPath, tables.ImpactedPath.idpath == imp_hls1.idpath)
        ).join(
            (subquery, tables.ImpactedPath.idsupitem == subquery.c.idsupitem)
        ).group_by(imp_hls1.idpath, subquery.c.idcorrevent
        ).subquery()

        # Requête récupérant les noms des SHN de plus haut niveau
        # impactés par chacun des évènements passés en paramètre.
        # Fait appel à la sous-requête précédente (subquery2).
        services = DBSession.query(
            tables.HighLevelService.servicename,
            subquery2.c.idcorrevent
        ).distinct(
        ).join(
            (imp_hls2, tables.HighLevelService.idservice == imp_hls2.idhls),
            (subquery2, subquery2.c.idpath == imp_hls2.idpath),
        ).filter(imp_hls2.distance == subquery2.c.distance
        ).order_by(
            tables.HighLevelService.servicename.asc()
        ).all()

        # Construction d'un dictionnaire associant à chaque évènement
        # le nom des SHN de plus haut niveau qu'il impacte.
        hls = {}
        for event_id in events_ids:
            hls[event_id] = []
        for service in services:
            hls[service.idcorrevent].append(service.servicename)

        return hls

# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2016 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Un plugin pour VigiBoard qui ajoute une colonne avec le nom de l'hôte
sur lequel porte l'événement corrélé.
"""
import tw.forms as twf
from tg.i18n import lazy_ugettext as l_
from sqlalchemy.sql.expression import union_all
from sqlalchemy.orm import aliased

from vigilo.models.session import DBSession
from vigilo.models import tables
from vigiboard.controllers.plugins import VigiboardRequestPlugin, INNER

class PluginMap(VigiboardRequestPlugin):
    """
    Ajoute de quoi filtrer sur les cartes.
    """
    def get_search_fields(self):
        return [
            twf.HiddenField(
                'idmap',
                validator=twf.validators.Int(if_missing=None),
            )
        ]

    def handle_search_fields(self, query, search, state, subqueries):
        if state != INNER or not search.get('idmap'):
            return
        idmap = int(search['idmap'])

        # Il s'agit d'un manager. On applique le filtre
        # indépendamment aux 2 sous-requêtes.
        if len(subqueries) == 2:
            mapnodells = DBSession.query(
                tables.MapNodeLls.idservice
            ).filter(tables.MapNodeLls.idmap == idmap).subquery()

            mapnodehost = DBSession.query(
                tables.MapNodeHost.idhost
            ).filter(tables.MapNodeHost.idmap == idmap).subquery()

            subqueries[0] = subqueries[0].join(
                    (mapnodells, mapnodells.c.idservice ==
                        tables.LowLevelService.idservice),
                )

            subqueries[1] = subqueries[1].join(
                    (mapnodehost, mapnodehost.c.idhost ==
                        tables.Host.idhost),
                )

        # Il s'agit d'un utilisateur normal.
        else:
            mapnodells = DBSession.query(
                tables.MapNodeLls.idservice.label('idsupitem')
            ).filter(tables.MapNodeLls.idmap == idmap)

            mapnodehost = DBSession.query(
                tables.MapNodeHost.idhost.label('idsupitem')
            ).filter(tables.MapNodeHost.idmap == idmap)

            union = union_all(mapnodells, mapnodehost, correlate=False).alias()
            subqueries[0] = subqueries[0].join(
                    (union, union.c.idsupitem == tables.UserSupItem.idsupitem),
                )


# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Modèle pour la table GraphToGroups"""

from sqlalchemy.orm import mapper
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String

from vigiboard.model import metadata

from vigiboard.config.vigiboard_config import vigiboard_config
# Generation par SQLAutoCode

graphtogroups =  Table(
    vigiboard_config['vigiboard_bdd.basename'] + 'graphtogroups',
    metadata,
    Column(u'graphname',
        String(length=100, convert_unicode=False, assert_unicode=None),
        ForeignKey(vigiboard_config['vigiboard_bdd.basename'] + 'graph.name'),
        primary_key=True, nullable=False),
    Column(u'groupname',
        String(length=100, convert_unicode=False, assert_unicode=None),
        ForeignKey(vigiboard_config['vigiboard_bdd.basename'] + \
                'graphgroups.name'),
        primary_key=True, nullable=False),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

# Classe a mapper

class GraphToGroups(object):
    """
    Classe liée avec la table associée
    """
    
    def __init__(self, graphname, groupname):
        self.graphname = graphname
        self.groupname = groupname


mapper(GraphToGroups, graphtogroups)

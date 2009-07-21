/vigiboard_config\['vigiboard_bdd.basename'\]/vigicore_config\['vigicore_bdd.basename'\]/g -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Modèle pour la table GraphGroups"""

from sqlalchemy.orm import mapper
from sqlalchemy import Table, Column
from sqlalchemy.types import Integer, String

from vigiboard.model import metadata

from vigiboard.config.vigilo_conf.vigicore import vigicore_config
# Generation par SQLAutoCode

graphgroups = Table(vigicore_config['vigicore_bdd.basename'] + 'graphgroups',
        metadata,
        Column(u'name',
            String(length=100, convert_unicode=True, assert_unicode=None),
            primary_key=True, nullable=False),
        Column(u'parent', Integer(), primary_key=False, nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

# Classe a mapper

class GraphGroups(object):
    """
    Classe liée avec la table associée
    """
    
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent

mapper(GraphGroups, graphgroups)

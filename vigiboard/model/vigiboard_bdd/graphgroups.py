# -*- coding: utf-8 -*-
"""Model For GraphGroups Table"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKeyConstraint, Column
from sqlalchemy.types import Integer, String, Text, DateTime

from vigiboard.model import metadata

from tg import config

# Generation par SQLAutoCode

graphgroups =  Table(config['vigiboard_bdd.basename'] + 'graphgroups', metadata,
            Column(u'graphname', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
            Column(u'idgraphgroup', Integer(), primary_key=True, nullable=False),
            Column(u'parent', Integer(), primary_key=False, nullable=False),
	    ForeignKeyConstraint([u'graphname'], [config['vigiboard_bdd.basename'] + u'graph.name'], name=u'graphgroups_ibfk_1'),
    )

# Classe a mapper

class GraphGroups(object):
	pass  
mapper(GraphGroups,graphgroups)



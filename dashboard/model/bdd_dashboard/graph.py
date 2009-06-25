# -*- coding: utf-8 -*-
"""Model For Graph Table"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKeyConstraint, Column
from sqlalchemy.types import Integer, String, Text, DateTime

from dashboard.model import metadata


# Generation par SQLAutoCode

graph =  Table('graph', metadata,
	    Column(u'name', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
            Column(u'template', String(length=2500, convert_unicode=False, assert_unicode=None), primary_key=False, nullable=False),
            Column(u'vlabel', String(length=2500, convert_unicode=False, assert_unicode=None), primary_key=False, nullable=False),
    )

# Classe a mapper

class Graph(object):
	pass  
mapper(Graph,graph)



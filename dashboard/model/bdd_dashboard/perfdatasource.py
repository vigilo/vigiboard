# -*- coding: utf-8 -*-
"""Model For PerfDataSource Table"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKeyConstraint, Column, Index
from sqlalchemy.types import Integer, String, Text, DateTime, Float

from dashboard.model import metadata


# Generation par SQLAutoCode

perfdatasource =  Table('perfdatasource', metadata,
	    Column(u'hostname', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
            Column(u'servicename', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
            Column(u'graphname', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=False, nullable=False),
            Column(u'type', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=False, nullable=False),
            Column(u'label', String(length=255, convert_unicode=False, assert_unicode=None), primary_key=False),
            Column(u'factor', Float(precision=None, asdecimal=False), primary_key=False, nullable=False),
	    ForeignKeyConstraint([u'hostname'], [u'host.name'], name=u'perfdatasource_ibfk_1'),
            ForeignKeyConstraint([u'graphname'], [u'graph.name'], name=u'perfdatasource_ibfk_3'),
            ForeignKeyConstraint([u'servicename'], [u'service.name'], name=u'perfdatasource_ibfk_2'),
    )
Index(u'graphname', perfdatasource.c.graphname, unique=False)
Index(u'servicename', perfdatasource.c.servicename, unique=False)

# Classe a mapper

class PerfDataSource(object):
	pass  
mapper(PerfDataSource,perfdatasource)



# -*- coding: utf-8 -*-
"""Model For ServiceTopo Table"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKeyConstraint, Column
from sqlalchemy.types import Integer, String, Text, DateTime

from dashboard.model import metadata


# Generation par SQLAutoCode

servicetopo =  Table('servicetopo', metadata,
	    Column(u'servicename', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
            Column(u'function', String(length=50, convert_unicode=False, assert_unicode=None), primary_key=False, nullable=False),
	    ForeignKeyConstraint([u'servicename'], [u'servicehautniveau.servicename'], name=u'servicetopo_ibfk_1'),
    )

# Classe a mapper

class ServiceTopo(object):
	pass  
mapper(ServiceTopo,servicetopo)



# -*- coding: utf-8 -*-
"""Model For ServiceHautNiveau Table"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKeyConstraint, Column, Index
from sqlalchemy.types import Integer, String, Text, DateTime

from dashboard.model import metadata


# Generation par SQLAutoCode

servicehautniveau =  Table('servicehautniveau', metadata,
	    Column(u'servicename', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
            Column(u'servicename_dep', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
	    ForeignKeyConstraint([u'servicename'], [u'service.name'], name=u'servicehautniveau_ibfk_1'),
            ForeignKeyConstraint([u'servicename_dep'], [u'service.name'], name=u'servicehautniveau_ibfk_2'),
    )
Index(u'servicename_dep', servicehautniveau.c.servicename_dep, unique=False)

# Classe a mapper

class ServiceHautNiveau(object):
	pass  
mapper(ServiceHautNiveau,servicehautniveau)



# -*- coding: utf-8 -*-
"""Model For Service Table"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKeyConstraint, Column, Index
from sqlalchemy.types import Integer, String, Text, DateTime

from dashboard.model import metadata


# Generation par SQLAutoCode
service =  Table('service', metadata,
	    Column(u'name', String(length=255, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
            Column(u'type', String(length=255, convert_unicode=False, assert_unicode=None), primary_key=False, nullable=False),
            Column(u'command', String(length=255, convert_unicode=False, assert_unicode=None), primary_key=False, nullable=False),
    )
Index(u'name', service.c.name, unique=False)

# Classe a mapper

class Service(object):
	pass  
mapper(Service,service)



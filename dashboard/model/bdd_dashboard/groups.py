# -*- coding: utf-8 -*-
"""Model For Groups Table"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKeyConstraint, Column, Index
from sqlalchemy.types import Integer, String, Text, DateTime

from dashboard.model import metadata


# Generation par SQLAutoCode

groups =  Table('groups', metadata,
	    Column(u'name', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
            Column(u'parent', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=False),
	    ForeignKeyConstraint([u'parent'], [u'groups.name'], name=u'groups_ibfk_1'),
    )
Index(u'parent', groups.c.parent, unique=False)

# Classe a mapper

class Groups(object):
	pass  
mapper(Groups,groups)

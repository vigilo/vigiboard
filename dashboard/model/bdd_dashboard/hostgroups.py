# -*- coding: utf-8 -*-
"""Model For HostGroups Table"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKeyConstraint, Column, Index
from sqlalchemy.types import Integer, String, Text, DateTime

from dashboard.model import metadata


# Generation par SQLAutoCode

hostgroups =  Table('hostgroups', metadata,
	    Column(u'hostname', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
            Column(u'groupname', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
	    ForeignKeyConstraint([u'hostname'], [u'host.name'], name=u'hostgroups_ibfk_1'),
            ForeignKeyConstraint([u'groupname'], [u'groups.name'], name=u'hostgroups_ibfk_2'),
    )
Index(u'groupname', hostgroups.c.groupname, unique=False)

# Classe a mapper

class HostGroups(object):
	pass  
mapper(HostGroups,hostgroups)



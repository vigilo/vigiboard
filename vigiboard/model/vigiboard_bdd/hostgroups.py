# -*- coding: utf-8 -*-
"""Model For HostGroups Table"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKeyConstraint, Column, Index
from sqlalchemy.types import Integer, String, Text, DateTime

from vigiboard.model import metadata

from tg import config

# Generation par SQLAutoCode

hostgroups =  Table(config['vigiboard_bdd.basename'] + 'hostgroups', metadata,
	    Column(u'hostname', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
            Column(u'groupname', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
	    ForeignKeyConstraint([u'hostname'], [config['vigiboard_bdd.basename'] + u'host.name'], name=u'hostgroups_ibfk_1'),
            ForeignKeyConstraint([u'groupname'], [config['vigiboard_bdd.basename'] + u'groups.name'], name=u'hostgroups_ibfk_2'),
    )
Index(u'groupname', hostgroups.c.groupname, unique=False)

# Classe a mapper

class HostGroups(object):
	pass  
mapper(HostGroups,hostgroups)



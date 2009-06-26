# -*- coding: utf-8 -*-
"""Model For ServiceGroups Table"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKeyConstraint, Column, Index
from sqlalchemy.types import Integer, String, Text, DateTime

from vigiboard.model import metadata

from tg import config

# Generation par SQLAutoCode

servicegroups =  Table(config['vigiboard_bdd.basename'] + 'servicegroups', metadata,
	    Column(u'servicename', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
            Column(u'groupname', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
	    ForeignKeyConstraint([u'servicename'], [config['vigiboard_bdd.basename'] + u'service.name'], name=u'servicegroups_ibfk_1'),
            ForeignKeyConstraint([u'groupname'], [config['vigiboard_bdd.basename'] + u'groups.name'], name=u'servicegroups_ibfk_2'),
    )
Index(u'groupname', servicegroups.c.groupname, unique=False
		)
# Classe a mapper

class ServiceGroups(object):
	pass  
mapper(ServiceGroups,servicegroups)



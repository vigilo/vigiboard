# -*- coding: utf-8 -*-
"""Model For Host Table"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKeyConstraint, Column, Index
from sqlalchemy.types import Integer, String, Text, DateTime

from vigiboard.model import metadata

from tg import config

# Generation par SQLAutoCode

host =  Table(config['vigiboard_bdd.basename'] + 'host', metadata,
	    Column(u'name', String(length=255, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
            Column(u'checkhostcmd', String(length=255, convert_unicode=False, assert_unicode=None), primary_key=False, nullable=False),
            Column(u'community', String(length=255, convert_unicode=False, assert_unicode=None), primary_key=False, nullable=False),
            Column(u'fqhn', String(length=255, convert_unicode=False, assert_unicode=None), primary_key=False, nullable=False),
            Column(u'hosttpl', String(length=255, convert_unicode=False, assert_unicode=None), primary_key=False, nullable=False),
            Column(u'mainip', String(length=255, convert_unicode=False, assert_unicode=None), primary_key=False, nullable=False),
            Column(u'port', Integer(), primary_key=False, nullable=False),
            Column(u'snmpoidsperpdu', Integer(), primary_key=False),
            Column(u'snmpversion', String(length=255, convert_unicode=False, assert_unicode=None), primary_key=False),
    )
Index(u'name', host.c.name, unique=False)

# Classe a mapper

class Host(object):
	pass  
mapper(Host,host)



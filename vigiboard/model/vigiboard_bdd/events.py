# -*- coding: utf-8 -*-
"""Model For Events Table"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKeyConstraint, Column, Index, DefaultClause, ForeignKey
from sqlalchemy.types import Integer, String, Text, DateTime, Boolean

from sqlalchemy.databases.mysql import MSEnum

from vigiboard.model import metadata
from tg import config
from datetime import datetime

# Generation par SQLAutoCode

events =  Table(config['vigiboard_bdd.basename'] + 'events', metadata,
    	    Column(u'idevent', Integer(), primary_key=True, nullable=False),
            Column(u'hostname', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=False, nullable=False),
            Column(u'servicename', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=False),
	    Column(u'server_source', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=False),
	    Column(u'severity', Integer(), primary_key=False, nullable=False),
	    Column(u'status', MSEnum('None','Acknowledged','AAClosed'), primary_key=False, nullable=False, server_default=DefaultClause('None', for_update=False)),
	    Column(u'active', Boolean(), primary_key=False, server_default=DefaultClause('TRUE', for_update=False)),
	    Column(u'timestamp', DateTime(timezone=False), primary_key=False),
            Column(u'output', Text(length=None, convert_unicode=False, assert_unicode=None), primary_key=False, nullable=False),
            Column(u'event_timestamp', DateTime(timezone=False), primary_key=False),
            Column(u'last_check', DateTime(timezone=False), primary_key=False),
            Column(u'recover_output', Text(length=None, convert_unicode=False, assert_unicode=None), primary_key=False),
            Column(u'timestamp_active', DateTime(timezone=False), primary_key=False),
            Column(u'timestamp_cleared', DateTime(timezone=False), primary_key=False),
            Column(u'trouble_ticket', String(length=20, convert_unicode=False, assert_unicode=None), primary_key=False),
            Column(u'occurence', Integer(), primary_key=False),
    	    ForeignKeyConstraint([u'servicename'], [config['vigiboard_bdd.basename'] + u'service.name'], name=u'events_ibfk_1'),
            ForeignKeyConstraint([u'hostname'], [config['vigiboard_bdd.basename'] + u'host.name'], name=u'events_ibfk_2')
    
    )

Index(u'hostname', events.c.hostname, events.c.servicename, unique=False)
Index(u'servicename', events.c.servicename, unique=False)

# Classe a mapper

class Events(object):

	def GetDate(self,element):
		element = self.__dict__[element]
		date = datetime.now() - element
		if date.days < 7 :
			return element.strftime('%a %H:%M:%S')
		else :	
			return element.strftime('%d %b %H:%M:%S')

	def GetSinceDate(self,element):
		date = datetime.now() - self.__dict__[element]
		minutes, seconds = divmod(date.seconds, 60)
		hours, minutes = divmod(minutes, 60)
		return "%dd %dh %d'" % (date.days , hours , minutes)

mapper(Events,events)

# -*- coding: utf-8 -*-
"""Model For EventHistory Table"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKeyConstraint, Column, Index
from sqlalchemy.types import Integer, String, Text, DateTime

from dashboard.model import metadata

from sqlalchemy.databases.mysql import MSEnum

import datetime

# Generation par SQLAutoCode

event_history =  Table('event_history', metadata,
            Column(u'idhistory', Integer(), primary_key=True, nullable=False),
	    Column(u'type_action', MSEnum('Nagios update state','Acknowlegement change state','New occurence','User comment','Ticket change','Oncall','Forced state'), primary_key=False, nullable=False),
            Column(u'idevent', Integer(), primary_key=False, nullable=False),
            Column(u'value', String(length=255, convert_unicode=False, assert_unicode=None), primary_key=False),
            Column(u'text', Text(length=None, convert_unicode=False, assert_unicode=None), primary_key=False),
            Column(u'timestamp', DateTime(timezone=False), default=datetime.datetime.now(),primary_key=False),
            Column(u'username', String(length=255, convert_unicode=False, assert_unicode=None), primary_key=False),
    	    ForeignKeyConstraint([u'idevent'], [u'events.idevent'], name=u'actions_ibfk_1'),
    
    )
Index(u'idevent', event_history.c.idevent, unique=False)

# Classe a mapper

class EventHistory(object):
	def __init__(self,type_action,idevent,value,text,username):
		self.type_action = type_action
		self.idevent = idevent
		self.value = value
		self.text = text
		self.username = username

mapper(EventHistory,event_history)


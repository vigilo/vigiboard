# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Modèle pour la table Service"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column, Index
from sqlalchemy.types import Integer, String, Text, DateTime

from vigiboard.model import metadata

from vigiboard.config.vigiboard_config import vigiboard_config

# Generation par SQLAutoCode

service =  Table(vigiboard_config['vigiboard_bdd.basename'] + 'service', metadata,
        Column(u'name', String(length=255, convert_unicode=True, assert_unicode=None), index=True,primary_key=True, nullable=False),
        Column(u'type', String(length=255, convert_unicode=True, assert_unicode=None), primary_key=False, nullable=False),
        Column(u'command', String(length=255, convert_unicode=True, assert_unicode=None), primary_key=False, nullable=False),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

# Classe a mapper

class Service(object):
    
    """
    Classe liée avec la table associée
    """
    
    def __init__(self,name,type=0,command=''):
        self.name = name
        self.type = type
        self.command = command
      
mapper(Service,service)



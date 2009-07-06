# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Modèle pour la table Groups"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column, Index
from sqlalchemy.types import Integer, String, Text, DateTime

from vigiboard.model import metadata

from vigiboard.config.vigiboard_config import vigiboard_config

# Generation par SQLAutoCode

groups =  Table(vigiboard_config['vigiboard_bdd.basename'] + 'groups', metadata,
        Column(u'name', String(length=100, convert_unicode=True, assert_unicode=None), primary_key=True, nullable=False),
        Column(u'parent', String(length=100, convert_unicode=True, assert_unicode=None), index=True,primary_key=False),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

# Classe a mapper

class Groups(object):
    
    """
    Classe liée avec la table associée
    """
    
    def __init__(self,name,parent=None):
        self.name = name
        self.parent = parent

mapper(Groups,groups)

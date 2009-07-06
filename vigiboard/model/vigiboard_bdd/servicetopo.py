# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Modèle pour la table ServiceTopo"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, String, Text, DateTime

from vigiboard.model import metadata

from vigiboard.config.vigiboard_config import vigiboard_config

# Generation par SQLAutoCode

servicetopo =  Table(vigiboard_config['vigiboard_bdd.basename'] + 'servicetopo', metadata,
        Column(u'servicename', String(length=100, convert_unicode=True, assert_unicode=None), ForeignKey(vigiboard_config['vigiboard_bdd.basename'] + u'servicehautniveau.servicename'),primary_key=True, nullable=False),
        Column(u'function', String(length=50, convert_unicode=True, assert_unicode=None), primary_key=False, nullable=False),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

# Classe a mapper

class ServiceTopo(object):
    
    """
    Classe liée avec la table associée
    """
    
    def __init__(self,servicename,function=''):
        self.servicename = servicename
        self.function = function

mapper(ServiceTopo,servicetopo)

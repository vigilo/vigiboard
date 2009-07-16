# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Modèle pour la table ServiceHautNiveau"""

from sqlalchemy.orm import mapper
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String
from vigiboard.model import metadata

from vigiboard.config.vigiboard_config import vigiboard_config

# Generation par SQLAutoCode

servicehautniveau = Table(
    vigiboard_config['vigiboard_bdd.basename'] + 'servicehautniveau',
    metadata,
    Column(u'servicename',
        String(length=100, convert_unicode=True, assert_unicode=None),
        ForeignKey(
            vigiboard_config['vigiboard_bdd.basename'] + u'service.name'
        ), primary_key=True, nullable=False),
    Column(u'servicename_dep',
        String(length=100, convert_unicode=True, assert_unicode=None),
        ForeignKey(
            vigiboard_config['vigiboard_bdd.basename'] + u'service.name'
        ), index=True ,primary_key=True, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)

# Classe a mapper

class ServiceHautNiveau(object):
    
    """
    Classe liée avec la table associée
    """
    
    def __init__(self, servicename, servicename_dep):
        self.servicename = servicename
        self.servicename_dep = servicename_dep

mapper(ServiceHautNiveau, servicehautniveau)

# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Modèle pour la table PerfDataSource"""

from sqlalchemy.orm import mapper
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Float
from vigiboard.model import metadata

from vigiboard.config.vigiboard_config import vigiboard_config

# Generation par SQLAutoCode

perfdatasource = Table(
    vigiboard_config['vigiboard_bdd.basename'] + 'perfdatasource',
    metadata,
    Column(u'hostname',
        String(length=100, convert_unicode=True, assert_unicode=None),
        ForeignKey(vigiboard_config['vigiboard_bdd.basename'] + u'host.name'),
        primary_key=True, nullable=False),
    Column(u'servicename',
        String(length=100, convert_unicode=True, assert_unicode=None),
        ForeignKey(
            vigiboard_config['vigiboard_bdd.basename'] + u'service.name'
        ), index=True, primary_key=True, nullable=False),
    Column(u'graphname',
        String(length=100, convert_unicode=True, assert_unicode=None),
        ForeignKey(vigiboard_config['vigiboard_bdd.basename'] + u'graph.name'),
        index=True,primary_key=False, nullable=False),
    Column(u'type',
        String(length=100, convert_unicode=True, assert_unicode=None),
        primary_key=False, nullable=False),
    Column(u'label',
        String(length=255, convert_unicode=True, assert_unicode=None),
        primary_key=False),
    Column(u'factor',
        Float(precision=None, asdecimal=False),
        primary_key=False, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)

# Classe a mapper

class PerfDataSource(object):
    
    """
    Classe liée avec la table associée
    """
    
    def __init__(self, hostname, servicename, graphname, typeperf = '',
            label = '', factor = 0.0):
        self.hostname = hostname
        self.servicename = servicename
        self.graphname = graphname
        self.type = typeperf
        self.label = label
        self.factor = factor

mapper(PerfDataSource, perfdatasource)

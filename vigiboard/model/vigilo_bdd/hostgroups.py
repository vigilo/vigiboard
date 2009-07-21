# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Modèle pour la table HostGroups"""

from sqlalchemy.orm import mapper
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String
from vigiboard.model import metadata

from vigiboard.config.vigilo_conf.vigicore import vigicore_config

# Generation par SQLAutoCode

hostgroups = Table(vigicore_config['vigicore_bdd.basename'] + 'hostgroups',
    metadata,
    Column(u'hostname',
        String(length=100, convert_unicode=True, assert_unicode=None),
        ForeignKey(vigicore_config['vigicore_bdd.basename'] + u'host.name'),
        primary_key=True, nullable=False),
    Column(u'groupname',
        String(length=100, convert_unicode=True, assert_unicode=None),
        ForeignKey(vigicore_config['vigicore_bdd.basename'] + u'groups.name'),
        index=True ,primary_key=True, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)

# Classe a mapper

class HostGroups(object):
    
    """
    Classe liée avec la table associée
    """
    
    def __init__(self, hostname, groupname):
        self.hostname = hostname
        self.groupname = groupname

mapper(HostGroups, hostgroups)



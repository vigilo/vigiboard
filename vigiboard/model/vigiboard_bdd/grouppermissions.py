# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Modèle pour la table GroupPermissions"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, String, Text, DateTime

from vigiboard.model import metadata, Permission

from vigiboard.model.vigiboard_bdd import Groups

from vigiboard.config.vigiboard_config import vigiboard_config

# Generation par SQLAutoCode

grouppermissions =  Table(vigiboard_config['vigiboard_bdd.basename'] + 'grouppermissions', metadata,
        Column(u'groupname', String(length=100, convert_unicode=True, assert_unicode=None), ForeignKey(vigiboard_config['vigiboard_bdd.basename'] +'groups.name'),primary_key=True, nullable=False),
        Column(u'idpermission', Integer(), autoincrement=False,primary_key=True, nullable=False),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

# Classe a mapper

class GroupPermissions(object):
    
    """
    Classe liée avec la table associée
    """

    def __init__(self,groupname,idpermission=0):
        self.groupname = groupname
        self.idpermission = idpermission

mapper(GroupPermissions,grouppermissions)

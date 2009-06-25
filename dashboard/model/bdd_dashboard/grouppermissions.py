# -*- coding: utf-8 -*-
"""Model For GroupPermissions Table"""

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKeyConstraint, Column
from sqlalchemy.types import Integer, String, Text, DateTime

from dashboard.model import metadata, Permission

from dashboard.model.bdd_dashboard import Groups

# Generation par SQLAutoCode
grouppermissions =  Table('grouppermissions', metadata,
	    Column(u'groupname', String(length=100, convert_unicode=False, assert_unicode=None), primary_key=True, nullable=False),
            Column(u'idpermission', Integer(), primary_key=True, nullable=False),
	    ForeignKeyConstraint([u'groupname'], [u'groups.name'], name=u'grouppermissions_ibfk_1'),
    )

# Classe a mapper

class GroupPermissions(object):
	def get_grp (self,user_p):
		events = DBSession.query(Groups).join(
			( GroupPermissions , Groups.name == GroupPermission.groupname ),
			( Permission , Permission.permission_id == GroupPermissions.idpermission )
			).filter(in_(Permission.permission_name,user_p))
		return events

mapper(GroupPermissions,grouppermissions)


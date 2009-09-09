# -*- coding: utf-8 -*-
"""The application's model objects"""

from vigilo.models.session import DBSession
from vigilo.models.vigilo_bdd_config import metadata

metadata.bind = DBSession.bind


from vigilo.models import User, UserGroup, Permission
from vigilo.models import Event, EventHistory
from vigilo.models import Graph, GraphGroup, GraphToGroups
from vigilo.models import Version, PerfDataSource, Group
from vigilo.models import Host, HostGroup
from vigilo.models import Service, ServiceGroup, \
                            ServiceHautNiveau, ServiceTopo


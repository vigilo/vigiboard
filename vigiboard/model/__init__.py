# -*- coding: utf-8 -*-
"""The application's model objects"""

from vigilo.models.session import DBSession
from vigilo.models.vigilo_bdd_config import metadata

metadata.bind = DBSession.bind


from vigilo.models import User, UserGroup, Permission
from vigilo.models import Events, EventHistory
from vigilo.models import Graph, GraphGroups, GraphToGroups
from vigilo.models import Version, PerfDataSource, Groups
from vigilo.models import Host, HostGroups
from vigilo.models import Service, ServiceGroups, \
                            ServiceHautNiveau, ServiceTopo


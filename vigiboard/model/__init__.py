# -*- coding: utf-8 -*-
"""The application's model objects"""

from vigilo.models.session import DBSession
from vigilo.models.vigilo_bdd_config import metadata

metadata.bind = DBSession.bind


from vigilo.models import User, UserGroup, Permission
from vigilo.models import Event, EventHistory, EventsAggregate
from vigilo.models import Graph, GraphGroup, GraphToGroups
from vigilo.models import Version, State, Statename, Group
from vigilo.models import Host, HostGroup
from vigilo.models import ServiceLowLevel, ServiceHighLevel, ServiceGroup
from vigilo.models import Access


# -*- coding: utf-8 -*-
"""The application's model objects"""

from vigilo.models.session import DBSession
from vigilo.models.vigilo_bdd_config import metadata

metadata.bind = DBSession.bind


from vigilo.models import User, UserGroup, Permission
from vigilo.models import Event, EventHistory, CorrEvent
from vigilo.models import Version, StateName, ApplicationLog
from vigilo.models import Host, HostGroup
from vigilo.models import LowLevelService, HighLevelService, ServiceGroup
from vigilo.models import ImpactedHLS, ImpactedPath


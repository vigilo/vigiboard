# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Test des modèle de Vigiboard"""

from nose.tools import eq_, assert_true

import re

from vigiboard.model import *
from vigiboard.tests.models import ModelTest


class TestEventHistory(ModelTest):
    """Test de la table EventHistory"""

    klass = EventHistory
    attrs = dict(type_action='Nagios update state',value='',text='',username='manager')

    def do_get_dependencies(self):
        DBSession.add(Host(name="monhost"))
        DBSession.add(Service(name="monservice"))
        DBSession.flush()
        DBSession.add(Events(hostname="monhost",servicename="monservice"))
        DBSession.flush()
        return dict(idevent=DBSession.query(Events.idevent)[0].idevent)

class TestEvent(ModelTest):
    """Test de la table Events"""

    klass = Events
    attrs = {}

    def do_get_dependencies(self):
        DBSession.add(Host(name="monhost"))
        DBSession.add(Service(name="monservice"))
        DBSession.flush()
        return dict(hostname="monhost",servicename="monservice")

    def test_get_date(self):
        """La fonction GetDate doit renvoyer un objet formaté"""
        assert_true(re.compile("^\w* \w* \d*:\d*:\d*$").match(self.obj.GetDate("timestamp_active")) or re.compile("^\w* \d*:\d*:\d*$").match(self.obj.GetDate("timestamp_active")))

    def test_get_since_date(self):
        """La fonction GetSinceDate doit renvoyer un objet formaté"""
        assert_true(re.compile("^\d*d \d*h \d'$").match(self.obj.GetSinceDate("timestamp_active")))
        
class TestGraph(ModelTest):
    """Test de la table GraphGroups"""

    klass = GraphGroups
    attrs = dict(name="mongraph")

class TestGraphToGroups(ModelTest):
    """Test de la table GraphToGroups"""

    klass = GraphToGroups
    attrs = {}

    def do_get_dependencies(self):
        DBSession.add(Graph(name="mongraph"))
        DBSession.add(GraphGroups(name="mongraphgroup"))
        DBSession.flush()
        return dict(graphname="mongraph",groupname="mongraphgroup")

class TestGraphGroups(ModelTest):
    """Test de la table GraphGroups"""

    klass = GraphGroups
    attrs = dict(name="mongraphgroup")

class TestGroupPermissions(ModelTest):
    """Test de la table GroupPermissions"""

    klass = GroupPermissions
    attrs = {}

    def do_get_dependencies(self):
        DBSession.add(Groups(name="mongroup"))
        DBSession.flush()
        return dict(groupname="mongroup")

class TestGroups(ModelTest):
    """Test de la table Groups"""

    klass = Groups
    attrs = dict(name="mongroup")

class TestHost(ModelTest):
    """Test de la table host"""

    klass = Host
    attrs = dict(name="monhost")

class TestHostGroups(ModelTest):
    """Test de la table hostgroup"""

    klass = HostGroups
    attrs = {}

    def do_get_dependencies(self):
        DBSession.add(Host(name="monhost"))
        DBSession.add(Groups(name="mongroup"))
        DBSession.flush()
        return dict(hostname="monhost",groupname="mongroup")

class TestPerfDataSource(ModelTest):
    """Test de la table perfdatasource"""

    klass = PerfDataSource
    attrs = {}

    def do_get_dependencies(self):
        DBSession.add(Host(name="monhost"))
        DBSession.add(Service(name="monservice"))
        DBSession.add(Graph(name="mongraph"))
        DBSession.flush()
        return dict(hostname="monhost",servicename="monservice",graphname="mongraph")

class TestServiceGroups(ModelTest):
    """Test de la table servicegroups"""

    klass = ServiceGroups
    attrs = {}

    def do_get_dependencies(self):
        DBSession.add(Service(name="monservice"))
        DBSession.add(Groups(name="mongroupe"))
        DBSession.flush()
        return dict(servicename="monservice",groupname="mongroupe")

class TestServiceHautNiveau(ModelTest):
    """Test de la table servicehautniveau"""

    klass = ServiceHautNiveau
    attrs = {}

    def do_get_dependencies(self):
        DBSession.add(Service(name="monservice"))
        DBSession.flush()
        return dict(servicename = "monservice", servicename_dep="monservice")

class TestService(ModelTest):
    """Test de la table service"""

    klass = Service
    attrs = dict(name="monservice")

class TestServiceTopo(ModelTest):
    """Test de la table servicetopo"""

    klass = ServiceTopo
    attrs = {}

    def do_get_dependencies(self):
        DBSession.add(Service(name="monservice"))
        DBSession.add(ServiceHautNiveau(servicename="monservice",servicename_dep="monservice"))
        DBSession.flush()
        return dict(servicename="monservice")

# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Test de la classe Vigiboard Request
"""

from nose.tools import assert_true
from datetime import datetime
import tg
import transaction

from vigiboard.model import DBSession, \
    Event, EventHistory, EventsAggregate, \
    Permission, User, StateName, \
    Group, Host, HostGroup, ServiceLowLevel, ServiceGroup
from vigiboard.tests import TestController
from vigiboard.controllers.vigiboardrequest import VigiboardRequest
from vigiboard.controllers.vigiboard_plugin.tests import MonPlugin


class TestVigiboardRequest(TestController):
    """Test de la classe Vigiboard Request"""

    def setUp(self):
        super(TestVigiboardRequest, self).setUp()

        # Les noms d'états.
        DBSession.add(StateName(statename=u'OK', order=0))
        DBSession.add(StateName(statename=u'WARNING', order=2))
        DBSession.flush()
        transaction.commit()

        # On peuple la base de données.

        # Les groupes et leurs dépendances
        self.editorsgroup = Group(name=u'editorsgroup')
        DBSession.add(self.editorsgroup)
        DBSession.flush()

        self.managersgroup = Group(name=u'managersgroup', parent=self.editorsgroup)
        DBSession.add(self.managersgroup)
        DBSession.flush()

        manage_perm = Permission.by_permission_name(u'manage')
        edit_perm = Permission.by_permission_name(u'edit')

        self.managersgroup.permissions.append(manage_perm)
        self.editorsgroup.permissions.append(edit_perm)
        DBSession.flush()

        # Les dépendances des événements
        host_template = {
            'checkhostcmd': u'halt',
            'snmpcommunity': u'public',
            'fqhn': u'localhost',
            'hosttpl': u'/dev/null',
            'mainip': u'192.168.1.1',
            'snmpport': 42,
        }

        service_template = {
            'command': u'halt',
            'op_dep': u'+',
        }

        DBSession.add(Host(name=u'managerhost', **host_template))
        DBSession.add(ServiceLowLevel(name=u'managerservice', **service_template))
        DBSession.add(Host(name=u'editorhost', **host_template))
        DBSession.add(ServiceLowLevel(name=u'editorservice', **service_template))
        DBSession.flush()

        # Table de jointure entre les hôtes/services et les groupes
        DBSession.add(HostGroup(hostname = u"managerhost",
            idgroup=self.managersgroup.idgroup))
        DBSession.add(HostGroup(hostname = u"editorhost",
            idgroup=self.editorsgroup.idgroup))
        DBSession.add(ServiceGroup(servicename = u"managerservice",
            idgroup=self.managersgroup.idgroup))
        DBSession.add(ServiceGroup(servicename = u"editorservice",
            idgroup=self.editorsgroup.idgroup))
        DBSession.flush()

        # Les événements eux-mêmes
        event_template = {
            'message': u'foo',
            'current_state': StateName.statename_to_value(u'WARNING'),
        }

        event1 = Event(hostname=u'managerhost',
            servicename=u'managerservice', **event_template)
        event2 = Event(hostname=u'editorhost',
            servicename=u'managerservice', **event_template)
        event3 = Event(hostname=u'managerhost',
            servicename=u'editorservice', **event_template)
        event4 = Event(hostname=u'editorhost',
            servicename=u'editorservice', **event_template)

        DBSession.add(event1)
        DBSession.add(event2)
        DBSession.add(event3)
        DBSession.add(event4)
        DBSession.flush()


        # Les historiques
        DBSession.add(EventHistory(type_action = u'Nagios update state',
            idevent=event1.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action = u'Acknowlegement change state',
            idevent=event1.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action = u'Nagios update state',
            idevent=event2.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action = u'Acknowlegement change state',
            idevent=event2.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action = u'Nagios update state',
            idevent=event3.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action = u'Acknowlegement change state',
            idevent=event3.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action = u'Nagios update state',
            idevent=event4.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action = u'Acknowlegement change state',
            idevent=event4.idevent, timestamp=datetime.now()))
        DBSession.flush()

        # Les événements corrélés
        aggregate_template = {
            'timestamp_active': datetime.now(),
            'priority': 1,
            'status': u'None',
        }
        self.aggregate1 = EventsAggregate(
            idcause=event1.idevent, **aggregate_template)
        self.aggregate2 = EventsAggregate(
            idcause=event4.idevent, **aggregate_template)

        self.aggregate1.events.append(event1)
        self.aggregate1.events.append(event3)
        self.aggregate2.events.append(event4)
        self.aggregate2.events.append(event2)
        DBSession.add(self.aggregate1)
        DBSession.add(self.aggregate2)
        DBSession.flush()

        for e in DBSession.query(Event).all():
            print "Event", e.idevent, e.hostname, e.servicename, e.current_state
        for ea in DBSession.query(EventsAggregate).all():
            print "EAggr", ea.idcause, ea.status
        for g in DBSession.query(Group).all():
            print "Group", g.idgroup, g.name, repr(g.idparent)
        for hg in DBSession.query(HostGroup).all():
            print "HGrup", hg.idgroup, hg.hostname
        for sg in DBSession.query(ServiceGroup).all():
            print "SGrup", sg.idgroup, sg.servicename
        transaction.commit()

    def tearDown(self):
        # This operation is only necessary for DBMS which are
        # really strict about table locks, such as PostgreSQL.
        # For our tests, we use an (in-memory) SQLite database,
        # so we're unaffected. This is done only for completeness.
        TestController.tearDown(self)


    def test_creation_requete(self):
        """Génération d'une requête avec plugin et permissions."""

        # On indique qui on est et on requête l'index pour obtenir
        # toutes les variables de sessions
        environ = {'REMOTE_USER': 'editor'}
        response = self.app.get('/', extra_environ=environ)
        tg.request = response.request

        # Derrière, VigiboardRequest doit charger le plugin de tests tout seul
        tg.config['vigiboard_plugins'] = [['tests', 'MonPlugin']]
        vigi_req = VigiboardRequest(User.by_user_name(u'editor'))

        # On effectue les tests suivants :
        #   le nombre de lignes (historique et événements) doivent
        #       correspondre (vérification des droits imposés par les groupes)
        #   le plugin fonctionne correctement

        num_rows = vigi_req.num_rows()
        assert_true(num_rows == 1, msg = "1 historique devrait " +
                "etre disponible pour l'utilisateur 'editor' mais il " +
                "y en a %d" % num_rows)

        vigi_req.format_events(0, 10)
        vigi_req.format_history()
        print vigi_req.events
        assert_true(len(vigi_req.events) == 1 + 1,
                msg = "1 evenement devrait etre disponible pour " +
                        "l'utilisateur 'editor' mais il y en a %d" %
                        (len(vigi_req.events) - 1))
        assert_true(vigi_req.events[1][6][0][0] != 'Error', 
                    msg = "Probleme d'execution des plugins ou de " +
                        "formatage des evenements") 

        # On recommence les tests précédents avec l'utilisateur
        # manager (plus de droits)

        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get('/', extra_environ=environ)
        tg.request = response.request

        vigi_req = VigiboardRequest(User.by_user_name(u'manager'))
        vigi_req.add_plugin(MonPlugin)

        num_rows = vigi_req.num_rows()
        assert_true(num_rows == 2, 
                msg = "2 historiques devraient etre disponibles pour " +
                        "l'utilisateur 'manager' mais il y en a %d" % num_rows)
        vigi_req.format_events(0, 10)
        vigi_req.format_history()
        assert_true(len(vigi_req.events) == 2 + 1, 
                msg = "2 evenements devraient être disponibles pour " +
                        "l'utilisateur 'manager' mais il y en a %d" %
                        (len(vigi_req.events) - 1))
        assert_true(vigi_req.events[1][6][0][0] != 'Error', 
                msg = "Probleme d'execution des plugins")


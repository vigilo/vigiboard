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
    Permission, User, \
    Group, Host, HostGroup, Service, ServiceGroup
from vigiboard.tests import TestController
from vigiboard.controllers.vigiboardrequest import VigiboardRequest
from vigiboard.controllers.vigiboard_plugin.tests import MonPlugin


class TestVigiboardRequest(TestController):
    """Test de la classe Vigiboard Request"""

    def setUp(self):
        TestController.setUp(self)

        # On peuple la base de données.

        # Les groupes et leurs dépendances
        hosteditors = Group(name=u'hosteditors')
        DBSession.add(hosteditors)
        DBSession.flush()

        hostmanagers = Group(name=u'hostmanagers', parent=hosteditors)
        DBSession.add(hostmanagers)
        DBSession.flush()

        manage_perm = Permission.by_permission_name(u'manage')
        edit_perm = Permission.by_permission_name(u'edit')

        manage_perm.groups.append(hostmanagers)
        edit_perm.groups.append(hosteditors)
        DBSession.flush()

        # Les dépendances des évènements
        host_template = {
            'checkhostcmd': u'halt',
            'snmpcommunity': u'public',
            'fqhn': u'localhost',
            'hosttpl': u'/dev/null',
            'mainip': u'192.168.1.1',
            'snmpport': 42,
        }

        service_template = {
            'servicetype': u'foo',
            'command': u'halt',
        }

        DBSession.add(Host(name=u'monhost', **host_template))
        DBSession.add(Service(name=u'monservice', **service_template))
        DBSession.add(Host(name=u'monhostuser', **host_template))
        DBSession.add(Service(name=u'monserviceuser', **service_template))
        DBSession.flush()

        # Table de jointure entre les hôtes/services et les groupes
        DBSession.add(HostGroup(hostname = u"monhost",
            groupname = u"hostmanagers"))
        DBSession.add(HostGroup(hostname = u"monhostuser",
            groupname = u"hosteditors"))
        DBSession.add(ServiceGroup(servicename = u"monservice",
            groupname = u"hostmanagers"))
        DBSession.add(ServiceGroup(servicename = u"monserviceuser",
            groupname = u"hosteditors"))
        DBSession.flush()

        # Les évènements eux-mêmes
        event_template = {
            'message': u'foo',
            'state': u'WARNING',
        }

        event1 = Event(idevent=u'event1', hostname=u'monhost',
            servicename=u'monservice', **event_template)
        event2 = Event(idevent=u'event2', hostname=u'monhostuser',
            servicename=u'monservice', **event_template)
        event3 = Event(idevent=u'event3', hostname=u'monhost',
            servicename=u'monserviceuser', **event_template)
        event4 = Event(idevent=u'event4', hostname=u'monhostuser',
            servicename=u'monserviceuser', **event_template)

        DBSession.add(event1)
        DBSession.add(event2)
        DBSession.add(event3)
        DBSession.add(event4)
        DBSession.flush()


        # Les historiques
        DBSession.add(EventHistory(type_action = u'Nagios update state',
            idevent = event1.idevent))
        DBSession.add(EventHistory(type_action = u'Acknowlegement change state',
            idevent = event1.idevent))
        DBSession.add(EventHistory(type_action = u'Nagios update state',
            idevent = event2.idevent))
        DBSession.add(EventHistory(type_action = u'Acknowlegement change state',
            idevent = event2.idevent))
        DBSession.add(EventHistory(type_action = u'Nagios update state',
            idevent = event3.idevent))
        DBSession.add(EventHistory(type_action = u'Acknowlegement change state',
            idevent = event3.idevent))
        DBSession.add(EventHistory(type_action = u'Nagios update state',
            idevent = event4.idevent))
        DBSession.add(EventHistory(type_action = u'Acknowlegement change state',
            idevent = event4.idevent))
        DBSession.flush()

        # Les évènements corrélés
        aggregate_template = {
            'timestamp_active': datetime.now(),
            'priority': 1,
            'status': u'None',
        }
        self.aggregate1 = EventsAggregate(
            idaggregate=u'foo',
            idcause=event1.idevent, **aggregate_template)
        self.aggregate2 = EventsAggregate(
            idaggregate=u'bar',
            idcause=event4.idevent, **aggregate_template)

        self.aggregate1.events.append(event1)
        self.aggregate1.events.append(event3)
        self.aggregate2.events.append(event4)
        self.aggregate2.events.append(event2)
        DBSession.add(self.aggregate1)
        DBSession.add(self.aggregate2)
        DBSession.flush()
        transaction.commit()


    def tearDown(self):
        # This operation is only necessary for DBMS which are
        # really strict about table locks, such as PostgreSQL.
        # For our tests, we use an (in-memory) SQLite database,
        # so we're unaffected. This is done only for completeness.
        DBSession.delete(self.aggregate1)
        DBSession.delete(self.aggregate1)
        DBSession.flush()
        transaction.commit()
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
        #   le nombre de lignes (historique et évènements) doivent
        #       correspondre (vérification des droits imposés par les groupes)
        #   le plugin fonctionne correctement

        num_rows = vigi_req.num_rows()
        assert_true(num_rows == 1, msg = "1 historique devrait " +
                "etre disponible pour l'utilisateur 'editor' mais il " +
                "y en a %d" % num_rows)
        vigi_req.format_events(0, 10)
        vigi_req.format_history()
        assert_true(len(vigi_req.events) == 1 + 1,
                msg = "1 evenement devrait etre disponible pour " +
                        "l'utilisateur 'editor' mais il y en a %d" %
                        len(vigi_req.events))
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
                        len(vigi_req.events))
        assert_true(vigi_req.events[1][6][0][0] != 'Error', 
                msg = "Probleme d'execution des plugins")


# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Tests portant sur la classe VigiboardRequest.
"""

from nose.tools import assert_true
from datetime import datetime
import tg
import transaction

from vigiboard.model import DBSession, \
    Event, EventHistory, CorrEvent, \
    Permission, User, StateName, \
    Host, HostGroup, ServiceLowLevel, ServiceGroup
from vigiboard.tests import TestController
from vigiboard.controllers.vigiboardrequest import VigiboardRequest
from vigiboard.controllers.vigiboard_plugin.tests import MonPlugin


class TestVigiboardRequest(TestController):
    """Test de la classe Vigiboard Request"""

    def setUp(self):
        """Création de données pour le test."""
        super(TestVigiboardRequest, self).setUp()

        # Les noms d'états.
        DBSession.add(StateName(statename=u'OK', order=0))
        DBSession.add(StateName(statename=u'WARNING', order=2))
        DBSession.flush()
        transaction.commit()

        # On peuple la base de données.

        # Les groupes et leurs dépendances
        self.hosteditors = HostGroup(name=u'editorsgroup')
        DBSession.add(self.hosteditors)
        self.hostmanagers = HostGroup(name=u'managersgroup',
            parent=self.hosteditors)
        DBSession.add(self.hostmanagers)
        self.serviceeditors = ServiceGroup(name=u'editorsgroup')
        DBSession.add(self.serviceeditors)
        self.servicemanagers = ServiceGroup(name=u'managersgroup',
            parent=self.serviceeditors)
        DBSession.add(self.servicemanagers)
        DBSession.flush()

        manage_perm = Permission.by_permission_name(u'manage')
        edit_perm = Permission.by_permission_name(u'edit')

        self.hostmanagers.permissions.append(manage_perm)
        self.hosteditors.permissions.append(edit_perm)
        self.servicemanagers.permissions.append(manage_perm)
        self.serviceeditors.permissions.append(edit_perm)
        DBSession.flush()

        # Création des hôtes de test.
        host_template = {
            'checkhostcmd': u'halt',
            'snmpcommunity': u'public',
            'hosttpl': u'/dev/null',
            'mainip': u'192.168.1.1',
            'snmpport': 42,
            'weight': 42,
        }

        managerhost = Host(name=u'managerhost', **host_template)
        editorhost = Host(name=u'editorhost', **host_template)
        DBSession.add(managerhost)
        DBSession.add(editorhost)

        # Création des services techniques de test.
        service_template = {
            'command': u'halt',
            'op_dep': u'+',
            'weight': 42,
        }

        service1 = ServiceLowLevel(
            host=managerhost,
            servicename=u'managerservice',
            **service_template
        )

        service2 = ServiceLowLevel(
            host=editorhost,
            servicename=u'managerservice',
            **service_template
        )

        service3 = ServiceLowLevel(
            host=managerhost,
            servicename=u'editorservice',
            **service_template
        )

        service4 = ServiceLowLevel(
            host=editorhost,
            servicename=u'editorservice',
            **service_template
        )

        DBSession.add(service1)
        DBSession.add(service2)
        DBSession.add(service3)
        DBSession.add(service4)
        DBSession.flush()

        # Affectation des hôtes/services aux groupes.
        self.hosteditors.hosts.append(editorhost)
        self.hostmanagers.hosts.append(managerhost)
        self.servicemanagers.services.append(service1)
        self.servicemanagers.services.append(service2)
        self.serviceeditors.services.append(service3)
        self.serviceeditors.services.append(service4)
        DBSession.flush()

        # Les événements eux-mêmes
        event_template = {
            'message': u'foo',
            'current_state': StateName.statename_to_value(u'WARNING'),
        }

        event1 = Event(supitem=service1, **event_template)
        event2 = Event(supitem=service2, **event_template)
        event3 = Event(supitem=service3, **event_template)
        event4 = Event(supitem=service4, **event_template)

        DBSession.add(event1)
        DBSession.add(event2)
        DBSession.add(event3)
        DBSession.add(event4)
        DBSession.flush()


        # Les historiques
        DBSession.add(EventHistory(type_action=u'Nagios update state',
            idevent=event1.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action=u'Acknowlegement change state',
            idevent=event1.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action=u'Nagios update state',
            idevent=event2.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action=u'Acknowlegement change state',
            idevent=event2.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action=u'Nagios update state',
            idevent=event3.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action=u'Acknowlegement change state',
            idevent=event3.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action=u'Nagios update state',
            idevent=event4.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action=u'Acknowlegement change state',
            idevent=event4.idevent, timestamp=datetime.now()))
        DBSession.flush()

        # Les événements corrélés
        aggregate_template = {
            'timestamp_active': datetime.now(),
            'priority': 1,
            'status': u'None',
        }
        self.aggregate1 = CorrEvent(
            idcause=event1.idevent, **aggregate_template)
        self.aggregate2 = CorrEvent(
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
        """Destruction des données temporaires du test."""
        # This operation is only necessary for DBMS which are
        # really strict about table locks, such as PostgreSQL.
        # For our tests, we use an (in-memory) SQLite database,
        # so we're unaffected. This is done only for completeness.
        TestController.tearDown(self)


    def test_request_creation(self):
        """Génération d'une requête avec plugin et permissions."""

        # On indique qui on est et on requête l'index pour obtenir
        # toutes les variables de sessions
        environ = {'REMOTE_USER': 'editor'}
        response = self.app.get('/', extra_environ=environ)
        tg.request = response.request

        # Derrière, VigiboardRequest doit charger le plugin de tests tout seul
        tg.config['vigiboard_plugins'] = [['tests', 'MonPlugin']]
        vigi_req = VigiboardRequest(User.by_user_name(u'editor'))
        vigi_req.add_table(
            CorrEvent,
            vigi_req.items.c.hostname,
            vigi_req.items.c.servicename,
        )
        vigi_req.add_join((Event, CorrEvent.idcause == Event.idevent))

        # On effectue les tests suivants :
        #   le nombre de lignes (historique et événements) doivent
        #       correspondre (vérification des droits imposés par les groupes)
        #   le plugin fonctionne correctement

        num_rows = vigi_req.num_rows()
        assert_true(num_rows == 1, 
            msg = "One history should be available for " +
            "the user 'editor' but there are %d" % num_rows)

        vigi_req.format_events(0, 10)
        vigi_req.format_history()
        assert_true(len(vigi_req.events) == 1 + 1,
            msg = "One history should be available for the user " +
            "'editor' but there are %d" % (len(vigi_req.events) - 1))
#        assert_true(vigi_req.events[1][6][0][0] != 'Error', 
#                    msg = "Plugins execution or events formatting problem") 

        # On recommence les tests précédents avec l'utilisateur
        # manager (plus de droits)

        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get('/', extra_environ=environ)
        tg.request = response.request

        vigi_req = VigiboardRequest(User.by_user_name(u'manager'))
        vigi_req.add_table(
            CorrEvent,
            vigi_req.items.c.hostname,
            vigi_req.items.c.servicename,
        )
        vigi_req.add_join((Event, CorrEvent.idcause == Event.idevent))
        vigi_req.add_plugin(MonPlugin)

        num_rows = vigi_req.num_rows()
        assert_true(num_rows == 2, 
            msg = "2 histories should be available for " +
            "the user 'manager' but there are %d" % num_rows)
        vigi_req.format_events(0, 10)
        vigi_req.format_history()
        assert_true(len(vigi_req.events) == 2 + 1, 
            msg = "2 histories should be available for the user " +
            "'manager' but there are %d" % (len(vigi_req.events) - 1))
#        assert_true(vigi_req.events[1][6][0][0] != 'Error', 
#                    msg = "Plugins execution or events formatting problem") 


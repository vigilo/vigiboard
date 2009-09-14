# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Test de la classe Vigiboard Request
"""
from nose.tools import assert_true

from vigiboard.model import DBSession, \
    Event, EventHistory, Permission, \
    Group, Host, HostGroup, Service, ServiceGroup
from vigiboard.tests import TestController
from vigiboard.controllers.vigiboardrequest import VigiboardRequest
from vigiboard.controllers.vigiboard_plugin.tests import MonPlugin
import tg
from nose.plugins.skip import SkipTest

class TestVigiboardRequest(TestController):
    """Test de la classe Vigiboard Request"""

    def test_creation_requete(self):
        """
        Génération d'une requête avec application d'un plugin et
        des permissions
        """

        # XXX This test has some issues, skip it until it gets fixed.
        raise SkipTest

        # On commence par peupler la base de donnée actuellement vide

        # les groups et leurs dépendances
        hostmanagers = Group(name=u'hostmanagers')
        hosteditors = Group(name=u'hosteditors', parent=hostmanagers)
        DBSession.add(hostmanagers)
        DBSession.add(hosteditors)

        manage_perm = Permission.by_name(u'manage')
        edit_perm = Permission.by_name(u'edit')

        manage_perm.groups.append(hostmanagers)
        edit_perm.groups.append(hosteditors)
        DBSession.flush()

        # Les évènements et leurs dépendances
        DBSession.add(Host(name = "monhost"))
        DBSession.add(Service(name = "monservice"))
        DBSession.add(Host(name = "monhostuser"))
        DBSession.add(Service(name = "monserviceuser"))
        DBSession.flush()
        event1 = Event(hostname = "monhost", servicename = "monservice")
        event2 = Event(hostname = "monhostuser", servicename = "monservice")
        event3 = Event(hostname = "monhost", servicename = "monserviceuser")
        event4 = Event(hostname = "monhostuser",
                servicename = "monserviceuser")

        # Les historiques
        DBSession.add(event1)
        DBSession.add(event2)
        DBSession.add(event3)
        DBSession.add(event4)
        DBSession.flush()
        DBSession.add(EventHistory(type_action = 'Nagios update state',
            idevent = event1.idevent))
        DBSession.add(EventHistory(type_action = 'Acknowlegement change state',
            idevent = event1.idevent))
        DBSession.add(EventHistory(type_action = 'Nagios update state',
            idevent = event2.idevent))
        DBSession.add(EventHistory(type_action = 'Acknowlegement change state',
            idevent = event2.idevent))
        DBSession.add(EventHistory(type_action = 'Nagios update state',
            idevent = event3.idevent))
        DBSession.add(EventHistory(type_action = 'Acknowlegement change state',
            idevent = event3.idevent))
        DBSession.add(EventHistory(type_action = 'Nagios update state',
            idevent = event4.idevent))
        DBSession.add(EventHistory(type_action = 'Acknowlegement change state',
            idevent = event4.idevent))
        
        # Table de jointure entre les hôtes et services et les groups
        DBSession.add(HostGroup(hostname = "monhost",
            groupname = "hostmanagers"))
        DBSession.add(HostGroup(hostname = "monhostuser",
            groupname = "hosteditors"))
        DBSession.add(ServiceGroup(servicename = "monservice",
            groupname = "hostmanagers"))
        DBSession.add(ServiceGroup(servicename = "monserviceuser",
            groupname = "hosteditors"))
        DBSession.flush()

        # On indique qui on est et on requête l'index pour obtenir
        # toutes les variables de sessions
        environ = {'REMOTE_USER': u'editor'}
        response = self.app.get('/', extra_environ=environ)
        tg.request = response.request

        vigi_req = VigiboardRequest()
        tg.config['vigiboard_plugins'] = [['tests', 'MonPlugin']]
        # Derrière, VigiboardRequest doit charger le plugin de test tout seul
        
        # On effectue les tests suivants :
        #   le nombre de lignes (historique et évènements) doivent
        #       correspondre (vérification des droits imposés par les groupes)
        #   le plugin fonctionne correctement

        num_rows = vigi_req.num_rows() 
        assert_true(num_rows == 2, msg = "2 historiques devrait " +\
                "être disponible pour l'utilisateur 'editor' mais il " +\
                "y en a %d" % num_rows)
        vigi_req.format_events(0, 10)
        vigi_req.format_history()
        assert_true(len(vigi_req.events) == 1 + 1, 
                msg = "1 évènement devrait être disponible pour " +\
                        "l'utilisateur 'editor' mais il y en a %d" % \
                        len(vigi_req.events))
        assert_true(vigi_req.events[1][6][0][0] != 'Error', 
                msg = "Problème d'exécution des plugins ou de " +\
                        "formatage des évènements") 

        # On recommence les tests précédents avec l'utilisateur
        # manager (plus de droits)

        environ = {'REMOTE_USER': u'manager'}
        response = self.app.get('/', extra_environ=environ)
        tg.request = response.request
        
        vigi_req = VigiboardRequest()
        
        vigi_req.add_plugin(MonPlugin)

        num_rows = vigi_req.num_rows()
        assert_true(num_rows == 8, 
                msg = "8 historiques devrait être disponible pour " +\
                        "l'utilisateur 'manager' mais il y en a %d" % num_rows)
        vigi_req.format_events(0, 10)
        vigi_req.format_history()
        assert_true(len(vigi_req.events) == 4 + 1, 
                msg = "4 évènement devrait être disponible pour " +\
                        "l'utilisateur 'editor' mais il y en a %d" % \
                        len(vigi_req.events))
        assert_true(vigi_req.events[1][6][0][0] != 'Error', 
                msg = "Problème d'exécution des plugins")


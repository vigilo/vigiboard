# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Test de la classe Vigiboard Request
"""
from nose.tools import assert_true

from vigiboard.model import DBSession, Events, EventHistory, Groups, \
    Permission, GroupPermissions, Host, Service, HostGroups, ServiceGroups
from vigiboard.tests import TestController
from vigiboard.controllers.vigiboardrequest import VigiboardRequest, \
            VigiboardRequestPlugin
from vigiboard.tests import teardown_db
import tg
import transaction


class TestVigiboardRequest(TestController):
    """Test de la classe Vigiboard Request"""

    def tearDown(self):
        """TearDown method for Nose"""

        DBSession.rollback()
        transaction.begin()
        teardown_db()

    def test_creation_requete(self):
        """
        Génération d'une requête avec application d'un plugin et
        des permissions
        """
        # On commence par peupler la base de donnée actuellement vide

        # les groups et leurs dépendances
        DBSession.add(Groups(name="hostmanagers"))
        DBSession.add(Groups(name="hosteditors", parent = "hostmanagers"))
        idmanagers = DBSession.query(Permission).filter(
                Permission.permission_name == 'manage')[0].permission_id
        ideditors = DBSession.query(Permission
                ).filter(Permission.permission_name == 'edit')[0].permission_id
        DBSession.add(GroupPermissions(groupname = "hostmanagers",
                idpermission = idmanagers))
        DBSession.add(GroupPermissions(groupname = "hosteditors",
                idpermission = ideditors))

        # Les évènements et leurs dépendances
        DBSession.add(Host(name = "monhost"))
        DBSession.add(Service(name = "monservice"))
        DBSession.add(Host(name = "monhostuser"))
        DBSession.add(Service(name = "monserviceuser"))
        DBSession.flush()
        event1 = Events(hostname = "monhost", servicename = "monservice")
        event2 = Events(hostname = "monhostuser", servicename = "monservice")
        event3 = Events(hostname = "monhost", servicename = "monserviceuser")
        event4 = Events(hostname = "monhostuser",
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
        DBSession.add(HostGroups(hostname = "monhost",
            groupname = "hostmanagers"))
        DBSession.add(HostGroups(hostname = "monhostuser",
            groupname = "hosteditors"))
        DBSession.add(ServiceGroups(servicename = "monservice",
            groupname = "hostmanagers"))
        DBSession.add(ServiceGroups(servicename = "monserviceuser",
            groupname = "hosteditors"))
        DBSession.flush()
        # On commit tout car app.get fait un rollback ou équivalent
        transaction.commit()
        # On indique qui on est et on requête l'index pour obtenir
        # toutes les variables de sessions
        environ = {'REMOTE_USER': 'editor'}
        response = self.app.get('/', extra_environ=environ)
        tg.request = response.request

        vigi_req = VigiboardRequest()
        tg.config['vigiboard_plugins'] = [['tests','MonPlugin']]
        # Derrière, VigiboardRequest doit charger le plugin de test tout seul
        
        # On effectu les tests suivants :
        #   le nombre de ligne (historique et évènements) doivent
        #       correspondre (vérification des droits imposé par les groupes)
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

        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get('/', extra_environ=environ)
        tg.request = response.request
        
        vigi_req = VigiboardRequest()
        
        vigi_req.add_plugin(MonPlugin(
            table = [EventHistory.idevent],
            join = [(EventHistory, EventHistory.idevent == Events.idevent)]))

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


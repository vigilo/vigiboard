# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Test de la classe Vigiboard Request pour des requêtes concernant les hôtes
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


class TestHostVigiboardRequest(TestController):
    """
    Test de la classe Vigiboard Request pour des requêtes concernant les hôtes
    """

    def setUp(self):
        super(TestHostVigiboardRequest, self).setUp()

        # On peuple la base de données.

        # On ajoute les noms d'états.
        DBSession.add(StateName(statename=u'OK', order=0))
        DBSession.add(StateName(statename=u'WARNING', order=2))
        DBSession.flush()
        transaction.commit()

        # On ajoute les groupes et leurs dépendances
        self.hosteditors = HostGroup(name=u'editorsgroup')
        DBSession.add(self.hosteditors)
        self.hostmanagers = HostGroup(name=u'managersgroup', parent=self.hosteditors)
        DBSession.add(self.hostmanagers)
        DBSession.flush()

        manage_perm = Permission.by_permission_name(u'manage')
        edit_perm = Permission.by_permission_name(u'edit')

        self.hostmanagers.permissions.append(manage_perm)
        self.hosteditors.permissions.append(edit_perm)
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

        # Affectation des hôtes aux groupes.
        self.hosteditors.hosts.append(editorhost)
        self.hostmanagers.hosts.append(managerhost)
        DBSession.flush()

        # Ajout des événements eux-mêmes
        event_template = {
            'message': u'foo',
            'current_state': StateName.statename_to_value(u'WARNING'),
        }
        event1 = Event(supitem=managerhost, **event_template)
        event2 = Event(supitem=editorhost, **event_template)
        DBSession.add(event1)
        DBSession.add(event2)
        DBSession.flush()

        # Ajout des historiques
        DBSession.add(EventHistory(type_action=u'Nagios update state',
            idevent=event1.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action=u'Acknowlegement change state',
            idevent=event1.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action=u'Nagios update state',
            idevent=event2.idevent, timestamp=datetime.now()))
        DBSession.add(EventHistory(type_action=u'Acknowlegement change state',
            idevent=event2.idevent, timestamp=datetime.now()))
        DBSession.flush()

        # Ajout des événements corrélés
        aggregate_template = {
            'timestamp_active': datetime.now(),
            'priority': 1,
            'status': u'None',
        }
        self.aggregate1 = CorrEvent(
            idcause=event1.idevent, **aggregate_template)
        self.aggregate2 = CorrEvent(
            idcause=event2.idevent, **aggregate_template)

        self.aggregate1.events.append(event1)
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
        TestController.tearDown(self)


    def test_request_creation(self):
        """Génération d'une requête avec plugin et permissions."""

        # On indique qui on est et on envoie une requête sur 
        # l'index pour obtenir toutes les variables de sessions.
        environ = {'REMOTE_USER': 'editor'}
        response = self.app.get('/', extra_environ=environ)
        tg.request = response.request

        # Derrière, VigiboardRequest doit charger le plugin de tests tout seul
        tg.config['vigiboard_plugins'] = [['tests', 'MonPlugin']]
        vigi_req = VigiboardRequest(User.by_user_name(u'editor'))
                
        print "\nPermissions sur l'hote 'editorhost' :"
        editorhost = DBSession.query(Host
                ).filter(Host.name == 'editorhost'
                ).one()
        for group in editorhost.groups:
            for permission in group.permissions:
                print permission.permission_name
               
        print "\nPermissions de l'utilisateur 'editor' :"
        editor = DBSession.query(User
                ).filter(User.user_name == 'editor'
                ).one()
        for group in editor.usergroups:
            for permission in group.permissions:
                print permission.permission_name
               
        print "\nNombre d'evenements dans la BDD : ", DBSession.query(Event).count()
        print "\nIds des evenements dans la BDD : "
        events = DBSession.query(Event)
        print "##### ", events[0].idevent, " ######"
        print "##### ", events[1].idevent, " ######"
               
        print "\nNombre d'evenements correles dans la BDD : ", DBSession.query(CorrEvent).count()
        aggregates = DBSession.query(CorrEvent)
        print "##### ", aggregates[0].events[0].idevent, " | ", aggregates[0].idcause, " ######"
        print "##### ", aggregates[1].events[0].idevent, " | ", aggregates[1].idcause, " ######"

        # On vérifie que le nombre d'événements corrélés 
        # trouvés par la requête est bien égal à 1.
        num_rows = vigi_req.num_rows()
        assert_true(num_rows == 1, msg = "La requete devrait retourner 1 " +
                "evenement correle pour l'utilisateur 'editor', " + 
                "mais ici elle en trouve %d" % num_rows)

        vigi_req.format_events(0, 10)
        vigi_req.format_history()
        assert_true(len(vigi_req.events) == 1 + 1,
                msg = "La requete devrait retourner 1 " +
                "evenement correle pour l'utilisateur 'editor', " + 
                "mais ici elle en trouve %d" %
                        (len(vigi_req.events) - 1))
        
        # On s'assure que le plugin fonctionne correctement
        assert_true(vigi_req.events[1][6][0][0] != 'Error', 
                    msg = "Probleme d'execution des plugins ou de " +
                        "formatage des evenements") 


        # On recommence les tests précédents avec l'utilisateur
        # manager (qui dispose de plus de droits).
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get('/', extra_environ=environ)
        tg.request = response.request

        vigi_req = VigiboardRequest(User.by_user_name(u'manager'))
        vigi_req.add_plugin(MonPlugin)

        # On vérifie que le nombre d'événements corrélés 
        # trouvés par la requête est bien égal à 2.
        num_rows = vigi_req.num_rows()
        assert_true(num_rows == 2, msg = "La requete devrait retourner 2 " +
                "evenement correle pour l'utilisateur 'editor', " + 
                "mais ici elle en trouve %d" % num_rows)

        vigi_req.format_events(0, 10)
        vigi_req.format_history()
        assert_true(len(vigi_req.events) == 2 + 1,
                msg = "La requete devrait retourner 2 " +
                "evenement correle pour l'utilisateur 'editor', " + 
                "mais ici elle en trouve %d" %
                        (len(vigi_req.events) - 1))
        
        # On s'assure que le plugin fonctionne correctement
        assert_true(vigi_req.events[1][6][0][0] != 'Error', 
                    msg = "Probleme d'execution des plugins ou de " +
                        "formatage des evenements") 


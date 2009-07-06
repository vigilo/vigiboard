# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Test de la classe Vigiboard Request
"""
from nose.tools import assert_true

from vigiboard.model import *
from vigiboard.tests import TestController
from vigiboard.controllers.vigiboard_ctl import VigiboardRequest, VigiboardRequestPlugin
from vigiboard.tests import setup_db, teardown_db
import tg
import transaction

#Create an empty database before we start our tests for this module
def setup():
    """Function called by nose on module load"""
    setup_db()

#Teardown that database 
def teardown():
    """Function called by nose after all tests in this module ran"""
    teardown_db()

class TestVigiboardRequest(TestController):

    def test_creation_requete(self):
        """Génération d'une requête avec application d'un plugin et des permissions"""

        # On commence par peupler la base de donnée actuellement vide

        # les groups et leurs dépendances
        DBSession.add(Groups(name="hostmanagers"))
        DBSession.add(Groups(name="hosteditors",parent="hostmanagers"))
        idmanagers = DBSession.query(Permission).filter(Permission.permission_name=='manage')[0].permission_id
        ideditors = DBSession.query(Permission).filter(Permission.permission_name=='edit')[0].permission_id
        DBSession.add(GroupPermissions(groupname="hostmanagers",idpermission=idmanagers))
        DBSession.add(GroupPermissions(groupname="hosteditors",idpermission=ideditors))

        # Les évènements et leurs dépendances
        DBSession.add(Host(name="monhost"))
        DBSession.add(Service(name="monservice"))
        DBSession.add(Host(name="monhostuser"))
        DBSession.add(Service(name="monserviceuser"))
        DBSession.flush()
        a = Events(hostname="monhost",servicename="monservice")
        b = Events(hostname="monhostuser",servicename="monservice")
        c = Events(hostname="monhost",servicename="monserviceuser")
        d = Events(hostname="monhostuser",servicename="monserviceuser")

        # Les historiques
        DBSession.add(a)
        DBSession.add(b)
        DBSession.add(c)
        DBSession.add(d)
        DBSession.flush()
        DBSession.add(EventHistory(type_action='Nagios update state',idevent=a.idevent))
        DBSession.add(EventHistory(type_action='Acknowlegement change state',idevent=a.idevent))
        DBSession.add(EventHistory(type_action='Nagios update state',idevent=b.idevent))
        DBSession.add(EventHistory(type_action='Acknowlegement change state',idevent=b.idevent))
        DBSession.add(EventHistory(type_action='Nagios update state',idevent=c.idevent))
        DBSession.add(EventHistory(type_action='Acknowlegement change state',idevent=c.idevent))
        DBSession.add(EventHistory(type_action='Nagios update state',idevent=d.idevent))
        DBSession.add(EventHistory(type_action='Acknowlegement change state',idevent=d.idevent))
        
        # Table de jointure entre les hôtes et services et les groups
        DBSession.add(HostGroups(hostname="monhost",groupname="hostmanagers"))
        DBSession.add(HostGroups(hostname="monhostuser",groupname="hosteditors"))
        DBSession.add(ServiceGroups(servicename="monservice",groupname="hostmanagers"))
        DBSession.add(ServiceGroups(servicename="monserviceuser",groupname="hosteditors"))
        DBSession.flush()
        
        # On commit tout car app.get fait un rollback ou équivalent
        transaction.commit()

        # On indique qui on est et on requête l'index pour obtenir toutes les variables de sessions
        environ = {'REMOTE_USER': 'editor'}
        response = self.app.get('/', extra_environ=environ)
        tg.request = response.request

        self.vr = VigiboardRequest()

        # On cré notre plugin, ici il ne sert qu'à lier l'historique avec chaque évènement
        class MonPlugin(VigiboardRequestPlugin):
            def show(self,rq):
                return rq[1]        
        
        self.vr.AddPlugin(MonPlugin(table=[EventHistory.idevent],
                                    join=[(EventHistory,EventHistory.idevent == Events.idevent)]))
        
        # On effectu les tests suivants :
        #   le nombre de ligne (historique et évènements) doivt correspondre (vérification des droits imposé par les groupes)
        #   le plugin fonctionne correctement
        nb = self.vr.NumRows() 
        assert_true(nb == 2,msg="2 historiques devrait être disponible pour l'utilisateur 'editor' mais il y en a %d" % nb)
        self.vr.FormatEvents(0,10)
        self.vr.FormatHistory()
        assert_true(len(self.vr.events) == 1+1,msg="1 évènement  devrait être disponible pour l'utilisateur 'editor' mais il y en a %d" % len(self.vr.events))
        assert_true(self.vr.events[1][6][0][0] != 'Error',msg="Problème d'exécution des plugins ou de formatage des évènements") 

        # On recommence les tests précédents avec l'utilisateur manager (plus de droits)
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get('/', extra_environ=environ)
        tg.request = response.request
        
        self.vr = VigiboardRequest()
        
        self.vr.AddPlugin(MonPlugin(table=[EventHistory.idevent],
                                    join=[(EventHistory,EventHistory.idevent == Events.idevent)]))

        nb = self.vr.NumRows()
        assert_true(nb == 8,msg="8 historiques devrait être disponible pour l'utilisateur 'manager' mais il y en a %d" % nb)
        self.vr.FormatEvents(0,10)
        self.vr.FormatHistory()
        assert_true(len(self.vr.events) == 4+1,msg="4 évènement  devrait être disponible pour l'utilisateur 'editor' mais il y en a %d" % len(self.vr.events))
        assert_true(self.vr.events[1][6][0][0] != 'Error',msg="Problème d'exécution des plugins")

# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Test du tableau d'événements de Vigiboard
"""

from nose.tools import assert_true, assert_equal
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

def populate_DB():
    """ Peuple la base de données. """

    # On ajoute des noms d'états.
    DBSession.add(StateName(statename = u'OK', order = 0))
    DBSession.add(StateName(statename = u'WARNING', order = 2))
    DBSession.flush()
    transaction.commit()

    # On ajoute un groupe d'hôtes et un groupe de services.
    hostmanagers = HostGroup(name = u'managersgroup')
    DBSession.add(hostmanagers)
    servicemanagers = ServiceGroup(name = u'managersgroup')
    DBSession.add(servicemanagers)
    DBSession.flush()

    # On ajoute la permission 'manage' à ces deux groupes.
    manage_perm = Permission.by_permission_name(u'manage')
    hostmanagers.permissions.append(manage_perm)
    servicemanagers.permissions.append(manage_perm)
    DBSession.flush()

    # On crée un hôte de test, et on l'ajoute au groupe d'hôtes.
    managerhost = Host(
        name = u'managerhost',      
        checkhostcmd = u'halt',
        snmpcommunity = u'public',
        hosttpl = u'/dev/null',
        mainip = u'192.168.1.1',
        snmpport = 42,
        weight = 42,
    )
    DBSession.add(managerhost)
    hostmanagers.hosts.append(managerhost)
    DBSession.flush()

    # On crée un services de bas niveau, et on l'ajoute au groupe de services.
    managerservice = ServiceLowLevel(
        host = managerhost,
        servicename = u'managerservice',
        command = u'halt',
        op_dep = u'+',
        weight = 42,
    )
    DBSession.add(managerservice)
    servicemanagers.services.append(managerservice)
    DBSession.flush()
    
    return (managerhost, managerservice)

def add_correvent_caused_by(supitem):
    """
    Ajoute dans la base de données un évènement corrélé causé 
    par un incident survenu sur l'item passé en paramètre.
    Génère un historique pour les tests.
    """

    # Ajout d'un événement
    event = Event(
        supitem = supitem, 
        message = u'foo',
        current_state = StateName.statename_to_value(u'WARNING'),
    )
    DBSession.add(event)
    DBSession.flush()

    # Ajout des historiques
    DBSession.add(EventHistory(
        type_action=u'Nagios update state',
        idevent=event.idevent, 
        timestamp=datetime.now()))
    DBSession.add(EventHistory(
        type_action=u'Acknowledgement change state',
        idevent=event.idevent, 
        timestamp=datetime.now()))
    DBSession.flush()

    # Ajout d'un événement corrélé
    aggregate = CorrEvent(
        idcause = event.idevent, 
        timestamp_active = datetime.now(),
        priority = 1,
        status = u'None')
    aggregate.events.append(event)
    DBSession.add(aggregate)
    DBSession.flush()
    
    return aggregate.idcorrevent
    

class TestEventTable(TestController):
    """
    Test des historiques de Vigiboard.
    """

    def test_event_caused_by_host_history_table(self):
        """
        Test de l'affichage du tableau d'historique
        d'un évènement corrélé causé par un hôte.
        """

        (managerhost, managerservice) = populate_DB()
        aggregate_id = add_correvent_caused_by(managerhost)
        
        #
        
        aggregates = DBSession.query(CorrEvent).count()
        print "Nombre d'evenements correles dans la BDD : ", aggregates 
        
        histories = DBSession.query(EventHistory).count()
        print "Nombre de lignes d'historique dans la BDD : ", histories 
        
        aggregate = DBSession.query(CorrEvent
            ).filter(CorrEvent.idcorrevent == aggregate_id).one()
        print "Permissions sur l'evenement correle : ",
        for group in aggregate.cause.supitem.groups:
            print "\n\tGroupe : ", group.name
            for permission in group.permissions:
                print "\t\t> ", permission.permission_name
          
        user = DBSession.query(User).filter(User.user_name == u"manager").one()      
        print "Permissions de l'utilisateur : ",
        for group in user.usergroups:
            print "\n\tGroupe : ", group.group_name
            for permission in group.permissions:
                print "\t\t> ", permission.permission_name
                
        
        #

        ### 1er cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'editor'.
        environ = {'REMOTE_USER': 'editor'}
        
        # On s'attend à ce qu'une erreur 302 soit renvoyée.
        response = self.app.get(
            '/event/' + str(aggregate_id),
            status = 302, 
            extra_environ = environ)

        ### 2nd cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'manager'.
        environ = {'REMOTE_USER': 'manager'}
        
        # On s'attend à ce que le statut de la requête soit 200.
        response = self.app.get(
            '/event/' + str(aggregate_id),
            status = 200, 
            extra_environ = environ)
        
#        response = self.app.get(
#            '/event/' + str(aggregate_id), extra_environ = environ)
#
#        # Il doit y avoir 2 lignes de résultats.
#        rows = response.lxml.xpath('//table[@class="history_table"]/tbody/tr')
#        print "There are %d rows in the result set" % len(rows)
#        assert_equal(len(rows), 2)




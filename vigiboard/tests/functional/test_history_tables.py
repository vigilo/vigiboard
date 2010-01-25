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
    Host, HostGroup, LowLevelService, ServiceGroup
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
    managerservice = LowLevelService(
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

def add_correvent_caused_by(supitem, 
        correvent_status=u"None", event_status=u"WARNING"):
    """
    Ajoute dans la base de données un évènement corrélé causé 
    par un incident survenu sur l'item passé en paramètre.
    Génère un historique pour les tests.
    """

    # Ajout d'un événement
    event = Event(
        supitem = supitem, 
        message = u'foo',
        current_state = StateName.statename_to_value(event_status),
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
        status = correvent_status)
    aggregate.events.append(event)
    DBSession.add(aggregate)
    DBSession.flush()
    
    return aggregate.idcorrevent
    

class TestEventTable(TestController):
    """
    Test des historiques de Vigiboard.
    """

    def test_host_event_history(self):
        """
        Test de l'affichage du tableau d'historique
        d'un évènement corrélé causé par un hôte.
        """

        # On peuple la BDD avec un hôte, un service de bas niveau,
        # et un groupe d'hôtes et de services associés à ces items.
        (managerhost, managerservice) = populate_DB()
        
        # On ajoute un évènement corrélé causé par l'hôte
        aggregate_id = add_correvent_caused_by(managerhost)
        
        transaction.commit()
        
        ### 1er cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'editor'.
        environ = {'REMOTE_USER': 'editor'}
        
        # On s'attend à ce qu'une erreur 302 soit renvoyée, et à
        # ce qu'un message d'erreur précise à l'utilisateur qu'il
        # n'a pas accès aux informations concernant cet évènement.
        response = self.app.get(
            '/event?idcorrevent=' + str(aggregate_id),
            status = 302, 
            extra_environ = environ)
        
        response = self.app.get(
            '/', 
            status = 200, 
            extra_environ = environ)
        assert_true(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]'))

        ### 2nd cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'manager'.
        environ = {'REMOTE_USER': 'manager'}
        
        # On s'attend à ce que le statut de la requête soit 200.
        response = self.app.get(
            '/event?idcorrevent=' + str(aggregate_id),
            status = 200, 
            extra_environ = environ)

        # Il doit y avoir 2 lignes de résultats.
        rows = response.lxml.xpath('//table[@class="history_table"]/tbody/tr')
        assert_equal(len(rows), 2)

    def test_service_event_history(self):
        """
        Test de l'affichage du tableau d'historique d'un
        évènement corrélé causé par un service de bas niveau.
        """

        # On peuple la BDD avec un hôte, un service de bas niveau,
        # et un groupe d'hôtes et de services associés à ces items.
        (managerhost, managerservice) = populate_DB()
        
        # On ajoute un évènement corrélé causé par le service
        aggregate_id = add_correvent_caused_by(managerservice)
        
        transaction.commit()
        
        ### 1er cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'editor'.
        environ = {'REMOTE_USER': 'editor'}
        
        # On s'attend à ce qu'une erreur 302 soit renvoyée, et à
        # ce qu'un message d'erreur précise à l'utilisateur qu'il
        # n'a pas accès aux informations concernant cet évènement.
        response = self.app.get(
            '/event?idcorrevent=' + str(aggregate_id),
            status = 302, 
            extra_environ = environ)
        
        response = self.app.get(
            '/', 
            status = 200, 
            extra_environ = environ)
        assert_true(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]'))

        ### 2nd cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'manager'.
        environ = {'REMOTE_USER': 'manager'}
        
        # On s'attend à ce que le statut de la requête soit 200.
        response = self.app.get(
            '/event?idcorrevent=' + str(aggregate_id),
            status = 200, 
            extra_environ = environ)

        # Il doit y avoir 2 lignes de résultats.
        rows = response.lxml.xpath('//table[@class="history_table"]/tbody/tr')
        assert_equal(len(rows), 2)

    def test_host_history(self):
        """
        Test de l'affichage du tableau d'historique
        des évènements corrélé d'un hôte donné.
        """

        # On peuple la BDD avec un hôte, un service de bas niveau,
        # et un groupe d'hôtes et de services associés à ces items.
        (managerhost, managerservice) = populate_DB()
        
        # On ajoute deux évènements corrélés causés par l'hôte :
        # le premier encore ouvert, le second clos par un utilisateur.
        aggregate_id1 = add_correvent_caused_by(managerhost)
        aggregate_id2 = add_correvent_caused_by(managerhost, u"AAClosed", 
                                                                        u"OK")
        
        transaction.commit()
        DBSession.add(managerhost)
        
        ### 1er cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'editor'.
        environ = {'REMOTE_USER': 'editor'}
        
        # On s'attend à ce qu'une erreur 302 soit renvoyée, et à
        # ce qu'un message d'erreur précise à l'utilisateur qu'il
        # n'a pas accès aux informations concernant cet évènement.
        response = self.app.get(
            '/host_service/' + managerhost.name,
            status = 302, 
            extra_environ = environ)
        
        response = self.app.get(
            '/', 
            status = 200, 
            extra_environ = environ)
        assert_true(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]'))

        ### 2nd cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'manager'.
        environ = {'REMOTE_USER': 'manager'}
        
        # On s'attend à ce que le statut de la requête soit 200.
        response = self.app.get(
            '/host_service/' + managerhost.name,
            status = 200, 
            extra_environ = environ)

        # Il doit y avoir 2 lignes d'évènements 
        # + 2 lignes contenant les tableaux d'historiques.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        assert_equal(len(rows), 2 + 2)
        # Et 4 lignes d'historiques dans les tableaux d'historiques.
        rows = response.lxml.xpath('//table[@class="history_table"]/tbody/tr')
        assert_equal(len(rows), 4)

    def test_service_history(self):
        """
        Test de l'affichage du tableau d'historique
        des évènements corrélé d'un service donné.
        """

        # On peuple la BDD avec un hôte, un service de bas niveau,
        # et un groupe d'hôtes et de services associés à ces items.
        (managerhost, managerservice) = populate_DB()
        
        # On ajoute deux évènements corrélés causés par le service :
        # le premier encore ouvert, le second clos par un utilisateur.
        aggregate_id1 = add_correvent_caused_by(managerservice)
        aggregate_id2 = add_correvent_caused_by(managerservice, u"AAClosed", 
                                                                        u"OK")
        
        transaction.commit()
        DBSession.add(managerhost)
        DBSession.add(managerservice)
        
        ### 1er cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'editor'.
        environ = {'REMOTE_USER': 'editor'}
        
        # On s'attend à ce qu'une erreur 302 soit renvoyée, et à
        # ce qu'un message d'erreur précise à l'utilisateur qu'il
        # n'a pas accès aux informations concernant cet évènement.
        response = self.app.get(
            '/host_service/' + managerhost.name 
                                + '/' + managerservice.servicename,
            status = 302, 
            extra_environ = environ)
        
        response = self.app.get(
            '/', 
            status = 200, 
            extra_environ = environ)
        assert_true(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]'))

        ### 2nd cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'manager'.
        environ = {'REMOTE_USER': 'manager'}
        
        # On s'attend à ce que le statut de la requête soit 200.
        response = self.app.get(
            '/host_service/' + managerhost.name 
                                + '/' + managerservice.servicename,
            status = 200, 
            extra_environ = environ)

        # Il doit y avoir 2 lignes d'évènements 
        # + 2 lignes contenant les tableaux d'historiques.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        assert_equal(len(rows), 2 + 2)
        # Et 4 lignes d'historiques dans les tableaux d'historiques.
        rows = response.lxml.xpath('//table[@class="history_table"]/tbody/tr')
        assert_equal(len(rows), 4)




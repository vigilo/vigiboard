# -*- coding: utf-8 -*-
"""
Teste le formulaire de recherche avec un nom de service.
"""
from nose.tools import assert_true, assert_equal
from datetime import datetime
import transaction

from vigiboard.tests import TestController
from vigiboard.model import DBSession, ServiceGroup, HostGroup, \
                            Host, Permission, StateName, \
                            ServiceLowLevel, Event, CorrEvent

def insert_deps():
    """Insère les dépendances nécessaires aux tests."""
    timestamp = datetime.now()
    DBSession.add(StateName(statename=u'OK', order=1))
    DBSession.add(StateName(statename=u'UNKNOWN', order=1))
    DBSession.add(StateName(statename=u'WARNING', order=1))
    DBSession.add(StateName(statename=u'CRITICAL', order=1))
    DBSession.flush()

    hostgroup = HostGroup(
        name=u'foo',
    )
    DBSession.add(hostgroup)

    host = Host(
        name=u'bar',
        checkhostcmd=u'',
        description=u'',
        hosttpl=u'',
        mainip=u'127.0.0.1',
        snmpport=42,
        snmpcommunity=u'public',
        snmpversion=u'3',
        weight=42,
    )
    DBSession.add(host)
    DBSession.flush()

    hostgroup.hosts.append(host)
    DBSession.flush()

    servicegroup = ServiceGroup(
        name=u'foo',
    )
    DBSession.add(servicegroup)

    service = ServiceLowLevel(
        host=host,
        command=u'',
        weight=42,
        servicename=u'baz',
        op_dep=u'&',
    )
    DBSession.add(service)
    DBSession.flush()

    servicegroup.services.append(service)
    DBSession.flush()

    event = Event(
        supitem=service,
        timestamp=timestamp,
        current_state=StateName.statename_to_value(u'WARNING'),
        message=u'Hello world',
    )
    DBSession.add(event)
    DBSession.flush()

    correvent = CorrEvent(
        impact=42,
        priority=42,
        trouble_ticket=None,
        status=u'None',
        occurrence=42,
        timestamp_active=timestamp,
        cause=event,
    )
    correvent.events.append(event)
    DBSession.add(correvent)
    DBSession.flush()
    return (hostgroup, servicegroup)

class TestSearchFormService(TestController):
    """Teste la récupération d'événements selon le groupe de services."""

    def test_search_service_when_allowed_by_hostgroup(self):
        """
        Teste la recherche par service avec des droits implicites
        (droits accordés car l'utilisateur a les droits sur l'hôte).
        """
        # On crée un service avec une alerte.
        # Le service est rattaché à un hôte appartenant
        # à un groupe d'hôtes pour lesquels l'utilisateur
        # a les permissions.
        hostgroup = insert_deps()[0]
        print "Adding permission for 'manager' on host group '%s'" % \
            hostgroup.name
        manage = Permission.by_permission_name(u'manage')
        manage.hostgroups.append(hostgroup)
        DBSession.flush()
        transaction.commit()

        # On envoie une requête avec recherche sur le service créé,
        # on s'attend à recevoir 1 résultat.
        response = self.app.get('/?service=baz',
            extra_environ={'REMOTE_USER': 'manager'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

    def test_search_service_when_allowed_by_servicegroup(self):
        """
        Teste la recherche par service avec des droits explicites
        (droits accordés car l'utilisateur a explicitement les droits
        sur ce service).
        """
        # On crée un service avec une alerte.
        # Le service est rattaché à un groupe de services
        # pour lesquel l'utilisateur a les permissions.
        servicegroup = insert_deps()[1]
        print "Adding permission for 'manager' on service group '%s'" % \
            servicegroup.name
        manage = Permission.by_permission_name(u'manage')
        manage.servicegroups.append(servicegroup)
        DBSession.flush()
        transaction.commit()

        # On envoie une requête avec recherche sur le service créé,
        # on s'attend à recevoir 1 résultat.
        response = self.app.get('/?service=baz',
            extra_environ={'REMOTE_USER': 'manager'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

    def test_search_inexistent_service(self):
        """Teste la recherche par service sur un service inexistant."""
        # On envoie une requête avec recherche sur un service
        # qui n'existe pas, on s'attend à n'obtenir aucun résultat.
        response = self.app.get('/?servicegroup=bad',
            extra_environ={'REMOTE_USER': 'manager'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

        # Il doit y avoir 1 seule colonne dans la ligne de résultats.
        # (la colonne contient le texte "Il n'y a aucun événément", traduit)
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        assert_equal(len(cols), 1)

    def test_search_service_when_disallowed(self):
        """Teste la recherche par service SANS les droits."""
        # On NE DONNE PAS l'autorisation aux utilisateurs
        # de voir l'alerte, donc elle ne doit jamais apparaître.
        insert_deps()
        transaction.commit()

        # On envoie une requête avec recherche sur le service créé,
        # mais avec un utilisateur ne disposant pas des permissions adéquates.
        # On s'attend à n'obtenir aucun résultat.
        response = self.app.get('/?hostgroup=baz',
            extra_environ={'REMOTE_USER': 'manager'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

        # Il doit y avoir 1 seule colonne dans la ligne de résultats.
        # (la colonne contient le texte "Il n'y a aucun événément", traduit)
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_equal(len(cols), 1)


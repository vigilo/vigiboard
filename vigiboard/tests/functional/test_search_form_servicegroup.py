# -*- coding: utf-8 -*-
"""
Teste le formulaire de recherche avec un groupe de services.
"""
from nose.tools import assert_true, assert_equal
from datetime import datetime
import transaction

from vigiboard.tests import TestController
from vigilo.models.configure import DBSession
from vigilo.models import ServiceGroup, Host, Permission, Event, \
                        LowLevelService, CorrEvent, StateName

def insert_deps():
    """Insère les dépendances nécessaires aux tests."""
    timestamp = datetime.now()

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

    servicegroup = ServiceGroup(
        name=u'foo',
    )
    DBSession.add(servicegroup)

    service = LowLevelService(
        host=host,
        command=u'',
        weight=42,
        servicename=u'baz',
        op_dep=u'&',
    )
    DBSession.add(service)
    DBSession.flush()

    servicegroup.services.append(service)
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
    return servicegroup

class TestSearchFormServiceGroup(TestController):
    """Teste la récupération d'événements selon le groupe de services."""

    def test_search_servicegroup_when_allowed(self):
        """Teste la recherche par servicegroup avec les bons droits d'accès."""
        # On crée un groupe de services appelé 'foo',
        # contenant un service 'bar', ainsi qu'un événement
        # et un événement corrélé sur ce service.
        # De plus, on donne l'autorisation aux utilisateurs
        # ayant la permission 'manage' de voir cette alerte.
        servicegroup = insert_deps()
        manage = Permission.by_permission_name(u'manage')
        manage.servicegroups.append(servicegroup)
        DBSession.flush()
        transaction.commit()

        # On envoie une requête avec recherche sur le groupe
        # de services créé, on s'attend à recevoir 1 résultat.
        response = self.app.get('/?servicegroup=foo',
            extra_environ={'REMOTE_USER': 'manager'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

    def test_search_inexistent_servicegroup(self):
        """Teste la recherche par servicegroup sur un groupe inexistant."""
        # On envoie une requête avec recherche sur un groupe de services
        # qui n'existe pas, on s'attend à n'obtenir aucun résultat.
        response = self.app.get('/?servicegroup=foot',
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

    def test_search_servicegroup_when_disallowed(self):
        """Teste la recherche par servicegroup SANS les droits d'accès."""
        # On crée un groupe de services appelé 'foo',
        # contenant un service 'bar', ainsi qu'un événement
        # et un événement corrélé sur cet hôte.
        # MAIS, on NE DONNE PAS l'autorisation aux utilisateurs
        # de voir cette alerte, donc elle ne doit jamais apparaître.
        insert_deps()
        transaction.commit()

        # On envoie une requête avec recherche sur le groupe de services
        # services créé, mais avec un utilisateur ne disposant pas des
        # permissions adéquates. On s'attend à n'obtenir aucun résultat.
        response = self.app.get('/?servicegroup=foo',
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


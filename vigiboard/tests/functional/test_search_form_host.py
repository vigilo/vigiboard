# -*- coding: utf-8 -*-
"""
Teste le formulaire de recherche avec un nom d'hôte.
"""
from nose.tools import assert_true, assert_equal
from datetime import datetime
import transaction

from vigiboard.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.tables import HostGroup, Host, Permission, \
                                    Event, CorrEvent, StateName

def insert_deps():
    """Insère les dépendances nécessaires aux tests."""
    timestamp = datetime.now()

    hostgroup = HostGroup(
        name=u'foo',
    )
    DBSession.add(hostgroup)
    DBSession.flush()

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

    event = Event(
        supitem=host,
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
    return hostgroup

class TestSearchFormHost(TestController):
    """Teste la récupération d'événements selon le nom d'hôte."""

    def test_search_host_when_allowed(self):
        """Teste la recherche par hôte avec les bons droits."""
        # On crée un hôte avec une alerte.
        # L'hôte est rattaché à un groupe d'hôtes
        # pour lesquel l'utilisateur a les permissions.
        hostgroup = insert_deps()
        manage = Permission.by_permission_name(u'manage')
        manage.hostgroups.append(hostgroup)
        DBSession.flush()
        transaction.commit()

        # On envoie une requête avec recherche sur l'hôte créé,
        # on s'attend à recevoir 1 résultat.
        response = self.app.get('/?host=bar',
            extra_environ={'REMOTE_USER': 'manager'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

    def test_search_inexistent_host(self):
        """Teste la recherche par hôte sur un hôte inexistant."""
        # On envoie une requête avec recherche sur un hôte
        # qui n'existe pas, on s'attend à n'obtenir aucun résultat.
        response = self.app.get('/?host=bad',
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

    def test_search_host_when_disallowed(self):
        """Teste la recherche par hôte SANS les droits."""
        # On NE DONNE PAS l'autorisation aux utilisateurs
        # de voir l'alerte, donc elle ne doit jamais apparaître.
        insert_deps()
        transaction.commit()

        # On envoie une requête avec recherche sur l'hôte créé,
        # mais avec un utilisateur ne disposant pas des permissions adéquates.
        # On s'attend à n'obtenir aucun résultat.
        response = self.app.get('/?host=bar',
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


# -*- coding: utf-8 -*-
"""
Teste le formulaire de recherche avec divers champs.
"""
from pylons.i18n import ugettext as _
from nose.tools import assert_true, assert_equal
from datetime import datetime
import transaction

from vigiboard.tests import TestController
from vigilo.models.configure import DBSession
from vigilo.models import HostGroup, Host, Permission, \
                            Event, CorrEvent, StateName

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

    hostgroup = HostGroup(
        name=u'foo',
    )
    hostgroup.hosts.append(host)
    DBSession.add(hostgroup)
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
        trouble_ticket=u'FOO BAR BAZ',
        status=u'None',
        occurrence=42,
        timestamp_active=timestamp,
        cause=event,
    )
    correvent.events.append(event)
    DBSession.add(correvent)
    DBSession.flush()

    # On attribut les permissions.
    manage = Permission.by_permission_name(u'manage')
    manage.hostgroups.append(hostgroup)
    DBSession.flush()
    return timestamp


class TestSearchFormMisc(TestController):
    """Teste la récupération d'événements selon le nom d'hôte."""
    def test_search_by_output(self):
        """Teste la recherche sur le message issu de Nagios."""
        insert_deps()
        transaction.commit()

        # Permet également de vérifier que la recherche est
        # insensible à la casse.
        response = self.app.get('/?output=hello',
            extra_environ={'REMOTE_USER': 'manager'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

    def test_search_by_trouble_ticket(self):
        """Teste la recherche sur le ticket d'incident."""
        insert_deps()
        transaction.commit()

        # Permet également de vérifier que la recherche est
        # insensible à la casse.
        response = self.app.get('/?trouble_ticket=bar',
            extra_environ={'REMOTE_USER': 'manager'})
        transaction.commit()

        # Il doit y avoir 1 seule ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

    def test_search_by_dates(self):
        """Teste la recherche par dates."""
        timestamp = insert_deps()
        transaction.commit()

        # Préparation des dates/heures.
        # On réutilise le formattage attendu par le contrôleur
        # (donc dépendant de la locale des tests, "fr" par défaut).
        # TRANSLATORS: Format de date et heure.
        from_date = timestamp.strftime(str(_("%Y-%m-%d %I:%M:%S %p")))
        # TRANSLATORS: Format de date et heure.
        to_date = datetime.max.strftime(str(_("%Y-%m-%d %I:%M:%S %p")))

        # Permet également de vérifier que la recherche
        # par date est inclusive.
        response = self.app.get(
            '/?from_date=%(from_date)s&to_date=%(to_date)s' % {
                'from_date': from_date,
                'to_date': to_date,
            },
            extra_environ={'REMOTE_USER': 'manager'})
        transaction.commit()

        # Il doit y avoir 1 seule ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)


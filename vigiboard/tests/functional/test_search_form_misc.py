# -*- coding: utf-8 -*-
# Copyright (C) 2006-2018 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Teste le formulaire de recherche avec divers champs.
"""
from __future__ import print_function
from nose.tools import assert_true, assert_equal
from datetime import datetime
from datetime import timedelta
import transaction

from vigiboard.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.tables import SupItemGroup, Host, Permission, \
                                    Event, CorrEvent, StateName, \
                                    User, UserGroup, DataPermission

def insert_deps():
    """Insère les dépendances nécessaires aux tests."""
    timestamp = datetime.now() + timedelta(seconds=-10)

    host = Host(
        name=u'bar',
        description=u'',
        hosttpl=u'',
        address=u'127.0.0.1',
        snmpport=42,
        snmpcommunity=u'public',
        snmpversion=u'3',
    )
    DBSession.add(host)
    DBSession.flush()

    hostgroup = SupItemGroup(name=u'foo', parent=None)
    hostgroup.supitems.append(host)
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
        priority=42,
        trouble_ticket=u'FOO BAR BAZ éçà',
        ack=CorrEvent.ACK_NONE,
        occurrence=42,
        timestamp_active=timestamp,
        cause=event,
    )
    correvent.events.append(event)
    DBSession.add(correvent)
    DBSession.flush()

    # On donne l'accès aux données.
    usergroup = UserGroup.by_group_name(u'users')
    DBSession.add(DataPermission(
        group=hostgroup,
        usergroup=usergroup,
        access=u'r',
    ))
    DBSession.flush()
    return timestamp

class TestSearchFormMisc(TestController):
    """Teste la récupération d'événements selon le nom d'hôte."""
    def setUp(self):
        super(TestSearchFormMisc, self).setUp()
        perm = Permission.by_permission_name(u'vigiboard-access')
        user = User(
            user_name=u'user',
            fullname=u'',
            email=u'some.random@us.er',
        )
        usergroup = UserGroup(group_name=u'users')
        user.usergroups.append(usergroup)
        usergroup.permissions.append(perm)
        DBSession.add(user)
        DBSession.add(usergroup)
        DBSession.flush()

    def get_number_of_rows(self, from_date, to_date):
        """Détermine le nombre de lignes parmi les résultats d'une recherche sur le formulaire."""
        response = self.app.get(
            '/?from_date=%(from_date)s&to_date=%(to_date)s' % {
                'from_date': from_date,
                'to_date': to_date,
            },
            extra_environ={'REMOTE_USER': 'user'})
        rows = self.get_rows(response)
        print("There are %d rows in the result set" % len(rows))
        return len(rows)

    def test_search_by_output(self):
        """Teste la recherche sur le message issu de Nagios."""
        insert_deps()
        transaction.commit()

        # Permet également de vérifier que la recherche est
        # insensible à la casse.
        response = self.app.get('/?output=hello*',
            extra_environ={'REMOTE_USER': 'user'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = self.get_rows(response)
        print("There are %d rows in the result set" % len(rows))
        assert_equal(len(rows), 1)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = self.get_cells(response)
        print("There are %d columns in the result set" % len(cols))
        assert_true(len(cols) > 1)

    def test_search_by_trouble_ticket(self):
        """Teste la recherche sur le ticket d'incident."""
        insert_deps()
        transaction.commit()

        # Permet également de vérifier que la recherche est
        # insensible à la casse.
        response = self.app.get('/?trouble_ticket=*bar*',
            extra_environ={'REMOTE_USER': 'user'})
        transaction.commit()

        # Il doit y avoir 1 seule ligne de résultats.
        rows = self.get_rows(response)
        print("There are %d rows in the result set" % len(rows))
        assert_equal(len(rows), 1)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = self.get_cells(response)
        print("There are %d columns in the result set" % len(cols))
        assert_true(len(cols) > 1)

    def test_search_by_dates(self):
        """Teste la recherche par dates."""
        timestamp = insert_deps()
        transaction.commit()

        # Préparation des dates/heures.
        from_date = timestamp.strftime("%Y-%m-%d %I:%M:%S %p")
        to_date = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

        # Permet également de vérifier que la recherche
        # par date est inclusive.
        response = self.app.get(
            '/?from_date=%(from_date)s&to_date=%(to_date)s' % {
                'from_date': from_date,
                'to_date': to_date,
            },
            extra_environ={'REMOTE_USER': 'user'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = self.get_rows(response)
        print("There are %d rows in the result set" % len(rows))
        assert_equal(len(rows), 1)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = self.get_cells(response)
        print("There are %d columns in the result set" % len(cols))
        assert_true(len(cols) > 1)

    def test_future_begin_date(self):
        """Contrôle des dates. Vérifie que date de début < date courante."""
        timestamp = insert_deps()
        transaction.commit()

        # Préparation des dates/heures.
        from_date = datetime.now() + timedelta(seconds=60)
        from_date = from_date.strftime("%Y-%m-%d %I:%M:%S %p")
        to_date = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

        # La recherche en utilisant une date de début supérieure
        # à la date actuelle doit générer une erreur/redirection.
        environ = {'REMOTE_USER': 'user'}
        resp = self.app.get(
            '/?from_date=%(from_date)s&to_date=%(to_date)s' % {
                'from_date': from_date,
                'to_date': to_date,
            },
            extra_environ=environ,
            status=302)

        # Après redirection, le message d'erreur apparait dans la page.
        resp = resp.follow(extra_environ=environ)
        error = '<div id="flash"><div class="error">%s</div></div>' % \
            'Start date cannot be greater than current date'
        assert_true(error in resp.body)

    def test_future_end_date(self):
        """Contrôle des dates. Vérifie que date de fin < date courante."""
        timestamp = insert_deps()
        transaction.commit()

        # Préparation des dates/heures.
        from_date = timestamp.strftime("%Y-%m-%d %I:%M:%S %p")
        to_date = datetime.now() + timedelta(seconds=60)
        to_date = to_date.strftime("%Y-%m-%d %I:%M:%S %p")

        # La recherche en utilisant une date de fin supérieure
        # à la date courante doit générer une erreur/redirection.
        environ = {'REMOTE_USER': 'user'}
        resp = self.app.get(
            '/?from_date=%(from_date)s&to_date=%(to_date)s' % {
                'from_date': from_date,
                'to_date': to_date,
            },
            extra_environ=environ,
            status=302)

        # Après redirection, le message d'erreur apparait dans la page.
        resp = resp.follow(extra_environ=environ)
        error = '<div id="flash"><div class="error">%s</div></div>' % \
            'End date cannot be greater than current date'
        assert_true(error in resp.body)

    def test_dates_inconsistency(self):
        """Contrôle des dates. Vérifie date de début <= date de fin."""
        timestamp = insert_deps()
        transaction.commit()

        # Préparation des dates/heures.
        from_date = timestamp + timedelta(seconds=5)
        from_date = from_date.strftime("%Y-%m-%d %I:%M:%S %p")
        to_date = timestamp.strftime("%Y-%m-%d %I:%M:%S %p")

        # La recherche en utilisant une date de début supérieure
        # à la date de fin doit générer une erreur/redirection.
        environ = {'REMOTE_USER': 'user'}
        resp = self.app.get(
            '/?from_date=%(from_date)s&to_date=%(to_date)s' % {
                'from_date': from_date,
                'to_date': to_date,
            },
            extra_environ=environ,
            status=302)

        # Après redirection, le message d'erreur apparait dans la page.
        resp = resp.follow(extra_environ=environ)
        error = '<div id="flash"><div class="error">%s</div></div>' % \
            'Start date cannot be greater than end date'
        assert_true(error in resp.body)


# -*- coding: utf-8 -*-
# Copyright (C) 2006-2018 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Teste le formulaire de recherche avec un nom de service.
"""
from __future__ import print_function
from nose.tools import assert_true, assert_equal
from datetime import datetime
import transaction

from vigiboard.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.demo import functions
from vigilo.models.tables import Permission, User, UserGroup, DataPermission


def insert_deps():
    """Insère les dépendances nécessaires aux tests."""
    timestamp = datetime.now()

    hostgroup = functions.add_supitemgroup(u'foo')
    host = functions.add_host(u'bar')
    hostgroup.supitems.append(host)
    DBSession.flush()

    servicegroup = functions.add_supitemgroup(u'bar')
    service = functions.add_lowlevelservice(host, u'baz')
    servicegroup.supitems.append(service)
    DBSession.flush()

    event = functions.add_event(service, u'WARNING', u'Hello world', timestamp)
    functions.add_correvent([event], timestamp=timestamp)
    return (hostgroup, servicegroup)


class TestSearchFormService(TestController):
    """Teste la récupération d'événements selon le groupe de services."""
    def setUp(self):
        super(TestSearchFormService, self).setUp()
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

    def test_search_service_when_allowed_by_host(self):
        """
        Teste la recherche par service avec des droits implicites
        (droits accordés car l'utilisateur a les droits sur l'hôte).
        """
        # On crée un service avec une alerte.
        # Le service est rattaché à un hôte appartenant
        # à un groupe d'hôtes pour lesquels l'utilisateur
        # a les permissions.
        hostgroup = insert_deps()[0]
        usergroup = UserGroup.by_group_name(u'users')
        DBSession.add(DataPermission(
            group=hostgroup,
            usergroup=usergroup,
            access=u'r',
        ))
        DBSession.flush()
        transaction.commit()

        # On envoie une requête avec recherche sur le service créé,
        # on s'attend à recevoir 1 résultat.
        response = self.app.get('/?service=baz',
            extra_environ={'REMOTE_USER': 'user'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = self.get_rows(response)
        print("There are %d rows in the result set" % len(rows))
        assert_equal(len(rows), 1)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = self.get_cells(response)
        print("There are %d columns in the result set" % len(cols))
        assert_true(len(cols) > 1)

    def test_search_service_when_allowed_by_service(self):
        """
        Teste la recherche par service avec des droits explicites
        (droits accordés car l'utilisateur a explicitement les droits
        sur ce service).
        """
        # On crée un service avec une alerte.
        # Le service est rattaché à un groupe de services
        # pour lesquel l'utilisateur a les permissions.
        servicegroup = insert_deps()[1]
        usergroup = UserGroup.by_group_name(u'users')
        DBSession.add(DataPermission(
            group=servicegroup,
            usergroup=usergroup,
            access=u'r',
        ))
        DBSession.flush()
        transaction.commit()

        # On envoie une requête avec recherche sur le service créé,
        # on s'attend à recevoir 1 résultat.
        response = self.app.get('/?service=baz',
            extra_environ={'REMOTE_USER': 'user'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = self.get_rows(response)
        print("There are %d rows in the result set" % len(rows))
        assert_equal(len(rows), 1)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = self.get_cells(response)
        print("There are %d columns in the result set" % len(cols))
        assert_true(len(cols) > 1)

    def test_search_inexistent_service(self):
        """Teste la recherche par service sur un service inexistant."""
        transaction.commit()
        # On envoie une requête avec recherche sur un service
        # qui n'existe pas, on s'attend à n'obtenir aucun résultat.
        response = self.app.get('/?service=bad',
            extra_environ={'REMOTE_USER': 'user'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = self.get_rows(response)
        print("There are %d rows in the result set" % len(rows))
        assert_equal(len(rows), 1)

        # Il doit y avoir 1 seule colonne dans la ligne de résultats.
        # (la colonne contient le texte "Il n'y a aucun événément", traduit)
        cols = self.get_cells(response)
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
        response = self.app.get('/?service=baz',
            extra_environ={'REMOTE_USER': 'user'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = self.get_rows(response)
        print("There are %d rows in the result set" % len(rows))
        assert_equal(len(rows), 1)

        # Il doit y avoir 1 seule colonne dans la ligne de résultats.
        # (la colonne contient le texte "Il n'y a aucun événément", traduit)
        cols = self.get_cells(response)
        print("There are %d columns in the result set" % len(cols))
        assert_equal(len(cols), 1)

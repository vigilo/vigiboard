# -*- coding: utf-8 -*-
# Copyright (C) 2006-2015 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

""" Test du plugin listant les services de haut niveau impactés. """

import transaction
from nose.tools import assert_equal

from vigilo.models.session import DBSession
from vigilo.models.demo import functions
from vigilo.models.tables import Permission, DataPermission, SupItemGroup, \
                            ImpactedPath, ImpactedHLS, User, UserGroup
from vigiboard.tests import TestController

def populate_DB():
    """ Peuple la base de données. """

    # On ajoute un groupe d'hôtes
    hostmanagers = SupItemGroup(name=u'managersgroup', parent=None)
    DBSession.add(hostmanagers)
    DBSession.flush()

    # On lui octroie les permissions
    usergroup = UserGroup.by_group_name(u'users_with_access')
    DBSession.add(DataPermission(
        group=hostmanagers,
        usergroup=usergroup,
        access=u'r',
    ))
    DBSession.flush()

    # On crée un hôte de test.
    host = functions.add_host(u'host')

    # On affecte cet hôte au groupe précédemment créé.
    hostmanagers.supitems.append(host)
    DBSession.flush()

    # On ajoute un évènement brut et un événement corrélé causé par cet hôte.
    event1 = functions.add_event(host, u'WARNING', u'foo')
    aggregate = functions.add_correvent([event1])

    transaction.commit()
    return aggregate

def add_paths(path_number, path_length, idsupitem):
    """
    Ajoute path_number chemins de services de haut niveau impactés
    dans la base de donnée. Leur longeur sera égale à path_length.
    La 3ème valeur passée en paramètre est l'id du supitem impactant.

    path_number * path_length services de
    haut niveau sont créés dans l'opération.
    """

    # Création des chemins de services de haut niveau impactés.
    for j in range(path_number):

        # On crée le chemin en lui-même
        path = ImpactedPath(idsupitem = idsupitem)
        DBSession.add(path)
        DBSession.flush()

        # Pour chaque étage du chemin,
        for i in range(path_length):
            # on ajoute un service de haut niveau dans la BDD...
            hls = functions.add_highlevelservice(
                u'HLS' + str(j + 1) + str(i + 1), None)

            # ...et on ajoute un étage au chemin contenant ce service.
            DBSession.add(
                ImpactedHLS(
                    path = path,
                    hls = hls,
                    distance = i + 1,
                ))

    DBSession.flush()
    transaction.commit()


class TestHLSPlugin(TestController):
    """
    Classe de test du contrôleur listant les services
    de haut niveau impactés par un évènement corrélé.
    """
    def setUp(self):
        super(TestHLSPlugin, self).setUp()
        perm = Permission.by_permission_name(u'vigiboard-access')

        user = User(
            user_name=u'access',
            fullname=u'',
            email=u'user.has@access',
        )
        usergroup = UserGroup(group_name=u'users_with_access')
        usergroup.permissions.append(perm)
        user.usergroups.append(usergroup)
        DBSession.add(user)
        DBSession.add(usergroup)
        DBSession.flush()

        self.aggregate = populate_DB()

    def test_no_impacted_hls(self):
        """
        Données affichées par le plugin HLS pour 0 HLS impacté
        Teste les données affichées par le  plugin lorsque
        aucun service de haut niveau n'est impacté.
        """

        # On peuple la base de données avant le test.
        DBSession.add(self.aggregate)
        add_paths(0, 0, self.aggregate.events[0].idsupitem)
        DBSession.add(self.aggregate)

        # On accède à la page principale de VigiBoard
        resp = self.app.post(
            '/', extra_environ={'REMOTE_USER': 'access'})

        # On s'assure que la colonne des HLS
        # impactés est vide pour notre évènement.
        plugin_data = resp.lxml.xpath('//table[@class="vigitable"]'
            '/tbody/tr/td[@class="plugin_hls"]/text()')
        assert_equal(plugin_data[0].strip(), "")

    def test_1_impacted_hls_path(self):
        """
        Données affichées par le plugin HLS pour 1 chemin impacté
        Teste les données affichées par le  plugin lorsque
        1 chemin de services de haut niveau est impacté.
        """

        # On peuple la base de données avant le test.
        DBSession.add(self.aggregate)
        add_paths(1, 2, self.aggregate.events[0].idsupitem)
        DBSession.add(self.aggregate)

        # On accède à la page principale de VigiBoard
        resp = self.app.post(
            '/', extra_environ={'REMOTE_USER': 'access'})

        # On s'assure que la colonne des HLS impactés contient
        # bien le nom de notre HLS de plus haut niveau impacté.
        plugin_data = resp.lxml.xpath('//table[@class="vigitable"]'
            '/tbody/tr/td[@class="plugin_hls"]/text()')
        assert_equal(plugin_data[0].strip(), "HLS12")

    def test_2_impacted_hls_path(self):
        """
        Données affichées par le plugin HLS pour 2 chemins impactés
        Teste les données affichées par le plugin lorsque
        2 chemins de services de haut niveau sont impactés.
        """

        # On peuple la base de données avant le test.
        DBSession.add(self.aggregate)
        add_paths(2, 2, self.aggregate.events[0].idsupitem)
        DBSession.add(self.aggregate)

        # On accède à la page principale de VigiBoard
        resp = self.app.post(
            '/', extra_environ={'REMOTE_USER': 'access'})

        # On s'assure que la colonne des HLS contient bien
        # le nombre de HLS de plus haut niveau impactés,
        plugin_data = resp.lxml.xpath('//table[@class="vigitable"]'
            '/tbody/tr/td[@class="plugin_hls"]/a/text()')
        assert_equal(plugin_data[0].strip(), "2")

    def test_same_hls_impacted_twice(self):
        """
        Pas de doublons dans les HLS impactés.
        Ticket #732.
        """

        # On peuple la base de données avant le test.
        DBSession.add(self.aggregate)
        hls = functions.add_highlevelservice(u'HLS', None, u'Bar')
        path1 = ImpactedPath(idsupitem = self.aggregate.events[0].idsupitem)
        DBSession.add(path1)
        path2 = ImpactedPath(idsupitem = self.aggregate.events[0].idsupitem)
        DBSession.add(path2)
        DBSession.flush()
        DBSession.add(
            ImpactedHLS(
                path = path1,
                hls = hls,
                distance = 1,
            )
        )
        DBSession.add(
            ImpactedHLS(
                path = path2,
                hls = hls,
                distance = 2,
            )
        )
        DBSession.flush()
        transaction.commit()
        DBSession.add(self.aggregate)

        # On accède à la page principale de VigiBoard
        resp = self.app.post(
            '/', extra_environ={'REMOTE_USER': 'access'})

        # On s'assure que la colonne des HLS contient bien
        # le nom de notre HLS de plus haut niveau impacté.
        plugin_data = resp.lxml.xpath('//table[@class="vigitable"]'
            '/tbody/tr/td[@class="plugin_hls"]/text()')
        assert_equal(plugin_data[0].strip(), "HLS")

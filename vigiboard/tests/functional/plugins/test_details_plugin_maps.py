# -*- coding: utf-8 -*-
# Copyright (C) 2006-2018 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Teste la partie "Cartes" du formulaire contenant les détails
pour un événement corrélé.
"""
from __future__ import print_function
from datetime import datetime
import transaction

from vigiboard.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.demo import functions
from vigilo.models import tables

class TestDetailsPluginMapsHostLimited(TestController):
    """
    Teste l'affichage des cartes dans le module de détails
    lorsqu'une limite à été réglée pour l'affichage.
    """
    application_under_test = 'limited_maps'
    # Seules les 2 premières cartes doivent figurer.
    # La 1ère correspond à la limite, la seconde permet
    # de détecter qu'il y avait plus de cartes que la limite.
    manager = [[1, 'M1'], [2, 'M2']]
    # L'utilisateur avec droits étendus voit
    # la même chose que le manager (2 cartes).
    unrestricted = manager[:]
    # L'utilisateur avec droits restreints ne voit
    # qu'une seule carte : "M2".
    restricted = [[2, 'M2']]
    supitem_class = tables.Host

    def shortDescription(self, *args, **kwargs):
        """Description courte du test en cours d'exécution."""
        res = TestController.shortDescription(*args, **kwargs)
        return "%s (limited + host)" % (res, )

    def setUp(self):
        """Initialisation avant chaque test."""
        super(TestDetailsPluginMapsHostLimited, self).setUp()
        # On fait manuellement ce que l'initialisation de VigiMap ferait
        # (car on est dans les tests de VigiBoard, pas ceux de VigiMap).
        root = functions.add_mapgroup(u'Root')
        DBSession.add(tables.Permission(permission_name=u'vigimap-access'))

        print("Creation hote, service et cartes")
        host = functions.add_host(u'localhost éçà')
        functions.add_lowlevelservice(host, u'lls éçà')
        sig = functions.add_supitemgroup(u'supitemgroup éçà')
        functions.add_host2group(host, sig)
        mg = functions.add_mapgroup(u'éçà', root)
        m1 = functions.add_map(u'M1', root)
        # La seconde carte appartient à "/Root/éçà"
        # et permet de tester les accès indirects.
        m2 = functions.add_map(u'M2', mg)
        m3 = functions.add_map(u'M3', root)

        # On ajoute l'hôte 2 fois sur M1 pour vérifier
        # l'absense de doublons dans les liens.
        print("Preparation cartes")
        functions.add_node_host(host, 'h1', m1)
        functions.add_node_host(host, 'h2', m1)
        functions.add_node_host(host, 'h', m2)
        functions.add_node_host(host, 'h', m3)

        # Création de quelques utilisateurs.
        print("Creation des comptes utilisateurs et reglages permissions")
        functions.add_user(u'restricted', u're@strict.ed',
                           u'restricted', u'restricted',
                           u'restricted')
        functions.add_user(u'unrestricted', u'unre@strict.ed',
                           u'unrestricted', u'unrestricted',
                           u'unrestricted')
        functions.add_user(u'no_rights', u'no_r@igh.ts',
                           u'no_rights', u'no_rights',
                           u'no_rights')
        # Les 3 utilisateurs ont accès à VigiBoard.
        functions.add_usergroup_permission(u'no_rights', u'vigiboard-access')
        functions.add_usergroup_permission(u'restricted', u'vigiboard-access')
        functions.add_usergroup_permission(u'unrestricted', u'vigiboard-access')
        # Mais seuls "restricted" et "unrestricted" ont accès à VigiMap.
        functions.add_usergroup_permission(u'restricted', u'vigimap-access')
        functions.add_usergroup_permission(u'unrestricted', u'vigimap-access')
        # Ils voient tous les trois les événements dans VigiBoard...
        functions.add_supitemgrouppermission(sig, 'no_rights')
        functions.add_supitemgrouppermission(sig, 'restricted')
        functions.add_supitemgrouppermission(sig, 'unrestricted')
        # ... mais "restricted" ne peut voir que "M2" ...
        functions.add_MapGroupPermission(mg, 'restricted')
        # ... tandis que "unrestricted" voit les 3 cartes (par héritage).
        functions.add_MapGroupPermission(root, 'unrestricted')

        DBSession.flush()
        transaction.commit()

    def tearDown(self):
        """Nettoyage après chaque test."""
        transaction.abort()
        DBSession.expunge_all()
        super(TestDetailsPluginMapsHostLimited, self).tearDown()

    def _insert_dep(self):
        """Insertion de l'événement corrélé de test."""
        print("Insertion evenement correle")
        timestamp = datetime.now()
        supitem = DBSession.query(self.supitem_class).one()
        if isinstance(supitem, tables.Host):
            event = functions.add_event(supitem, u'DOWN', u'', timestamp)
        else: # Sinon, il s'agit d'un LowLevelService.
            event = functions.add_event(supitem, u'CRITICAL', u'', timestamp)
        functions.add_correvent([event], timestamp=timestamp)
        DBSession.flush()
        transaction.commit()
        correvent = DBSession.query(tables.CorrEvent.idcorrevent).one()
        return correvent.idcorrevent

    def test_maps_links_anonymous(self):
        """Cartes dans dialogue détails en tant qu'anonyme."""
        idcorrevent = self._insert_dep()
        # 401 : Unauthorized car l'utilisateur doit s'authentifier
        # pour pouvoir accéder à la boîte de dialogue.
        self.app.post('/plugin_json', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, extra_environ={}, status=401)

    def test_maps_links_manager(self):
        """Cartes dans dialogue détails en tant que manager."""
        idcorrevent = self._insert_dep()
        response = self.app.post('/plugin_json', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, extra_environ={'REMOTE_USER': 'manager'})
        # Le manager a toujours accès à tout, la seule limite possible
        # est celle imposée par l'option "max_maps" dans la configuration.
        self.assertEquals(response.json['maps'], self.manager)

    def test_maps_links_no_rights(self):
        """Cartes dans dialogue détails sans droits."""
        idcorrevent = self._insert_dep()
        response = self.app.post('/plugin_json', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, extra_environ={'REMOTE_USER': 'no_rights'})
        # L'utilisateur n'a pas accès à VigiMap, donc il ne doit pas voir
        # les cartes, même s'il a accès à VigiBoard par ailleurs.
        self.assertEquals(response.json['maps'], [])

    def test_maps_links_restricted(self):
        """Cartes dans dialogue détails avec droits restreints."""
        idcorrevent = self._insert_dep()
        response = self.app.post('/plugin_json', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, extra_environ={'REMOTE_USER': 'restricted'})
        # L'utilisateur ne doit voir que les cartes pour lesquelles
        # il a été autorisé.
        self.assertEquals(response.json['maps'], self.restricted)

    def test_maps_links_unrestricted(self):
        """Cartes dans dialogue détails avec droits étendus."""
        idcorrevent = self._insert_dep()
        response = self.app.post('/plugin_json', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, extra_environ={'REMOTE_USER': 'unrestricted'})
        # L'utilisateur ne doit voir que les cartes pour lesquelles
        # il a été autorisé (les mêmes que que "restricted" + "M2").
        self.assertEquals(response.json['maps'], self.unrestricted)


class TestDetailsPluginMapsHostDisabled(TestDetailsPluginMapsHostLimited):
    """
    Teste la désactivation de l'affichage des cartes
    dans le module de détails.
    """
    application_under_test = 'disabled_maps'
    # La réponse ne doit contenir aucune carte,
    # quel que soit l'utilisateur qui interroge
    # VigiBoard (la fonctionnalité est désactivée).
    manager = []
    unrestricted = []
    restricted = []

    def shortDescription(self, *args, **kwargs):
        """Description courte du test en cours d'exécution."""
        res = TestController.shortDescription(*args, **kwargs)
        return "%s (disabled + host)" % (res, )


class TestDetailsPluginMapsHostUnlimited(TestDetailsPluginMapsHostLimited):
    """
    Teste l'affichage des cartes dans le module de détails
    lorsqu'il n'y a aucun limite.
    """
    application_under_test = 'unlimited_maps'
    # Le manager voit tout et en particulier les 3 cartes sur lesquelles
    # l'hôte apparaît. M1 ne doit apparaître qu'une seule fois
    # même si l'hôte est présent 2 fois sur la carte.
    manager = [[1, 'M1'], [2, 'M2'], [3, 'M3']]
    # L'utilisateur avec droits étendus voit
    # la même chose que le manager (3 cartes).
    unrestricted = manager[:]
    # L'utilisateur avec droits restreints ne voit pas 'M2'.
    restricted = [[2, 'M2']]

    def shortDescription(self, *args, **kwargs):
        """Description courte du test en cours d'exécution."""
        res = TestController.shortDescription(*args, **kwargs)
        return "%s (unlimited + host)" % (res, )

class TestDetailsPluginMapsServiceLimited(
    TestDetailsPluginMapsHostLimited):
    """
    Idem que la classe mère mais teste un événement corrélé
    portant sur un service de l'hôte plutôt que sur l'hôte lui-même.
    """
    supitem_class = tables.LowLevelService

    def shortDescription(self, *args, **kwargs):
        """Description courte du test en cours d'exécution."""
        # On court-circuite la hiérarchie de classes
        # pour appeler directement la méthode de nose/unittest.
        res = TestController.shortDescription(*args, **kwargs)
        return "%s (limited + service)" % (res, )

class TestDetailsPluginMapsServiceDisable(
    TestDetailsPluginMapsHostDisabled):
    """
    Idem que la classe mère mais teste un événement corrélé
    portant sur un service de l'hôte plutôt que sur l'hôte lui-même.
    """
    supitem_class = tables.LowLevelService

    def shortDescription(self, *args, **kwargs):
        """Description courte du test en cours d'exécution."""
        # On court-circuite la hiérarchie de classes
        # pour appeler directement la méthode de nose/unittest.
        res = TestController.shortDescription(*args, **kwargs)
        return "%s (disabled + service)" % (res, )

class TestDetailsPluginMapsServiceUnlimited(
    TestDetailsPluginMapsHostUnlimited):
    """
    Idem que la classe mère mais teste un événement corrélé
    portant sur un service de l'hôte plutôt que sur l'hôte lui-même.
    """
    supitem_class = tables.LowLevelService

    def shortDescription(self, *args, **kwargs):
        """Description courte du test en cours d'exécution."""
        # On court-circuite la hiérarchie de classes
        # pour appeler directement la méthode de nose/unittest.
        res = TestController.shortDescription(*args, **kwargs)
        return "%s (unlimited + service)" % (res, )

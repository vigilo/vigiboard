# -*- coding: utf-8 -*-
"""
Teste l'arbre de sélection des groupes du formulaire de recherche
"""
from nose.tools import assert_true, assert_equal
from datetime import datetime
import transaction

from vigiboard.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.tables import SupItemGroup, Host, Permission, StateName, \
                                    Event, CorrEvent, User, UserGroup, \
                                    DataPermission

from utils import populate_DB

class TestGroupSelectionTree(TestController):
    """Teste l'arbre de sélection des groupes du formulaire de recherche."""

    def setUp(self):
        super(TestGroupSelectionTree, self).setUp()
        populate_DB()

    def test_get_inexistent_group(self):
        """Récupération de l'étage de l'arbre pour un groupe inexistant"""

        # L'utilisateur est authentifié avec des permissions étendues.
        # Il cherche à obtenir la liste des groupes fils d'un groupe
        # qui n'existe pas, il ne doit donc obtenir aucun résultat.
        response = self.app.get('/get_groups?parent_id=%d' % -42,
            extra_environ={'REMOTE_USER': 'access'})
        json = response.json

        # On s'assure que la liste de groupes retournée est bien vide
        self.assertEqual(
            json, {'items': [], 'groups': []}
        )

        # L'utilisateur est authentifié et fait partie du groupe 'managers'.
        # Il cherche à obtenir la liste des groupes fils d'un groupe
        # qui n'existe pas, il ne doit donc obtenir aucun résultat.
        response = self.app.get('/get_groups?parent_id=%d' % -42,
            extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste de groupes retournée est bien vide
        self.assertEqual(
            json, {'items': [], 'groups': []}
        )

    def test_get_group_when_not_allowed(self):
        """Récupération de l'étage de l'arbre sans les droits"""

        # Récupération du groupe utilisé lors de ce test.
        group2 = SupItemGroup.by_group_name(u'group2')

        # L'utilisateur n'est pas authentifié.
        # Il cherche à obtenir la liste des groupes fils d'un groupe donné.
        response = self.app.get('/get_groups?parent_id=%d' % group2.idgroup,
            status=401)

        # L'utilisateur est authentifié avec des permissions
        # restreintes. Il cherche à obtenir la liste des groupes fils
        # d'un groupe auquel il n'a pas accès, même indirectement.
        response = self.app.get('/get_groups?parent_id=%d' % group2.idgroup,
            extra_environ={'REMOTE_USER': 'limited_access'})
        json = response.json

        # On s'assure que la liste de groupes retournée est bien vide
        self.assertEqual(
            json, {'items': [], 'groups': []}
        )

    def test_get_group_when_allowed(self):
        """Récupération de l'étage de l'arbre avec les droits"""

        # Récupération des groupes utilisés lors de ce test.
        root = SupItemGroup.by_group_name(u'root')
        maingroup = SupItemGroup.by_group_name(u'maingroup')
        group1 = SupItemGroup.by_group_name(u'group1')
        group2 = SupItemGroup.by_group_name(u'group2')

        # L'utilisateur est authentifié et fait partie du groupe 'managers'.
        # Il cherche à obtenir la liste des groupes fils d'un groupe donné.
        response = self.app.get('/get_groups?parent_id=%d' % root.idgroup,
            extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste retournée contient
        # bien les groupes fils de ce groupe parent
        self.assertEqual(
            json, {
                'items': [], 
                'groups': [
                    {'id': maingroup.idgroup, 'name': maingroup.name, 'type': 'group'}
                ]
            }
        )

        # L'utilisateur est authentifié avec des permissions
        # étendues. Il cherche à obtenir la liste des groupes
        # fils d'un groupe auquel il a directement accès.
        response = self.app.get('/get_groups?parent_id=%d' % root.idgroup,
            extra_environ={'REMOTE_USER': 'access'})
        json = response.json

        # On s'assure que la liste retournée contient
        # bien les groupes fils de ce groupe parent
        self.assertEqual(
            json, {
                'items': [], 
                'groups': [
                    {'id': maingroup.idgroup, 'name': maingroup.name, 'type': 'group'}
                ]
            }
        )

        # Le même utilisateur cherche à obtenir la liste des
        # groupes fils d'un groupe auquel il a indirectement accès.
        response = self.app.get('/get_groups?parent_id=%d' % maingroup.idgroup,
            extra_environ={'REMOTE_USER': 'access'})
        json = response.json

        # On s'assure que la liste retournée contient
        # bien les groupes fils de ce groupe parent.
        self.assertEqual(json, {
                'items': [], 
                'groups': [
                    {'id': group1.idgroup, 'name': group1.name, 'type': 'group'},
                    {'id': group2.idgroup, 'name': group2.name, 'type': 'group'}
                ]
            })

        # L'utilisateur est authentifié avec des permissions
        # restreintes. Il cherche à obtenir la liste des groupes
        # fils d'un groupe auquel il n'a pas accès, mais a toutefois
        # le droit d'accéder à un des groupes fils en question.
        response = self.app.get('/get_groups?parent_id=%d' % maingroup.idgroup,
            extra_environ={'REMOTE_USER': 'limited_access'})
        json = response.json

        # On s'assure que la liste retournée contient bien ce groupe fils.
        self.assertEqual(
            json, {
                'items': [], 
                'groups': [
                    {'id': group1.idgroup, 'name': group1.name, 'type': 'group'}
                ]
            }
        )

        # Le même utilisateur cherche à obtenir la liste des groupes
        # fils d'un groupe de niveau encore supérieur.
        response = self.app.get('/get_groups?parent_id=%d' % root.idgroup,
            extra_environ={'REMOTE_USER': 'limited_access'})
        json = response.json

        # On s'assure que la liste retournée contient bien
        # le groupe parent du groupe auquel il a accès.
        self.assertEqual(
            json, {
                'items': [], 
                'groups': [
                    {'id': maingroup.idgroup, 'name': maingroup.name, 'type': 'group'}
                ]
            }
        )

    def test_get_root_group_when_allowed(self):
        """Récupération des groupes racines de l'arbre avec les droits"""

        # Récupération du groupe utilisé lors de ce test.
        root = SupItemGroup.by_group_name(u'root')

        # L'utilisateur est authentifié et fait partie du groupe 'managers'.
        # Il cherche à obtenir la liste des groupes racines de l'arbre.
        response = self.app.get('/get_groups',
            extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste retournée contient bien le groupe racine.
        self.assertEqual(
            json, {
                'items': [], 
                'groups': [
                    {'id': root.idgroup, 'name': root.name, 'type': 'group'}
                ]
            }
        )

        # L'utilisateur est authentifié avec des permissions étendues.
        # Il cherche à obtenir la liste des groupes racines de l'arbre.
        response = self.app.get('/get_groups',
            extra_environ={'REMOTE_USER': 'access'})
        json = response.json

        # On s'assure que la liste retournée contient bien le
        # groupe racine, auquel cet utilisateur a directement accès.
        self.assertEqual(
            json, {
                'items': [], 
                'groups': [
                    {'id': root.idgroup, 'name': root.name, 'type': 'group'}
                ]
            }
        )

        # L'utilisateur est authentifié avec des permissions restreintes.
        # Il cherche à obtenir la liste des groupes racines de l'arbre.
        response = self.app.get('/get_groups',
            extra_environ={'REMOTE_USER': 'limited_access'})
        json = response.json

        # On s'assure que la liste retournée contient bien le
        # groupe racine, auquel cet utilisateur a indirectement accès.
        self.assertEqual(
            json, {
                'items': [], 
                'groups': [
                    {'id': root.idgroup, 'name': root.name, 'type': 'group'}
                ]
            }
        )

    def test_get_root_group_when_not_allowed(self):
        """Récupération des groupes racines de l'arbre sans les droits"""

        # Récupération du groupe utilisé lors de ce test.
        root = SupItemGroup.by_group_name(u'root')

        # L'utilisateur n'est pas authentifié, et cherche
        # à obtenir la liste des groupes racines de l'arbre.
        response = self.app.get('/get_groups', status=401)

        # Création d'un nouvel utilisateur et d'un nouveau groupe
        usergroup = UserGroup(group_name=u'new_users')
        vigiboard_perm = Permission.by_permission_name(u'vigiboard-access')
        usergroup.permissions.append(vigiboard_perm)
        user = User(
            user_name=u'new_user',
            fullname=u'',
            email=u'user.has.no@access',
        )
        user.usergroups.append(usergroup)
        DBSession.add(user)

        # L'utilisateur est authentifié mais n'a aucun accès. Il
        # cherche à obtenir la liste des groupes racines de l'arbre.
        response = self.app.get('/get_groups',
            extra_environ={'REMOTE_USER': 'new_user'})
        json = response.json

        # On s'assure que la liste retournée est bien vide.
        self.assertEqual(
            json, {
                'items': [], 
                'groups': []
            }
        )


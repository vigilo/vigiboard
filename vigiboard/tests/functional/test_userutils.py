# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Test de la classe User Utils
"""
import tg
import transaction
from nose.tools import assert_true

from vigiboard.model import DBSession, Group, Permission, User
from vigiboard.tests import TestController

class TestUserUtils(TestController):
    """Test retrieval of groups of hosts/services."""
    def test_groups_inheritance(self):
        """
        S'assure que les groupes sont correctement hérités.
        """

        # Création de 2 groupes d'utilisateurs.
        hosteditors = Group(name=u'hosteditors', parent=None)
        DBSession.add(hosteditors)

        hostmanagers = Group(name=u'hostmanagers', parent=hosteditors)
        DBSession.add(hostmanagers)

        # L'attribution des permissions.
        manage_perm = Permission.by_permission_name(u'manage')
        edit_perm = Permission.by_permission_name(u'edit')

        manage_perm.groups.append(hostmanagers)
        edit_perm.groups.append(hosteditors)
        DBSession.flush()
        transaction.commit()

        # On obtient les variables de session comme si on était loggué
        # en tant que manager.
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get('/', extra_environ=environ)
        
        # On récupère la liste des groups auxquels l'utilisateur appartient.
        username = response.request.environ \
            ['repoze.who.identity'] \
            ['repoze.who.userid']
        grp = User.by_user_name(username).groups

        # Permet de rafraîchir les instances.
        hostmanagers = DBSession.query(Group).filter(
                            Group.name==u'hostmanagers').one()
        hosteditors = DBSession.query(Group).filter(
                            Group.name==u'hosteditors').one()

        # On vérifie que la liste est correcte : le manager doit avoir accès
        # aux groupes 'hostmanagers' & 'hosteditors' (dont il hérite).
        assert_true(hostmanagers.idgroup in grp and
            hosteditors.idgroup in grp,
            msg = "il est dans %s" % grp)

        # On recommence avec l'utilisateur editor.
        environ = {'REMOTE_USER': 'editor'}
        response = self.app.get('/', extra_environ=environ)

        username = response.request.environ \
            ['repoze.who.identity'] \
            ['repoze.who.userid']
        grp = User.by_user_name(username).groups

        # L'utilisateur editor ne doit avoir accès qu'au groupe 'hosteditors'.
        assert_true(not(hostmanagers.idgroup in grp) and
            hosteditors.idgroup in grp,
            msg = "il est dans %s" % grp)


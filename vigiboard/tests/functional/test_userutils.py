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

    def setUp(self):
        TestController.setUp(self)

        # On commence par peupler la base.
        # Les groupes.
        self.hosteditors = Group(name=u'hosteditors', parent=None)
        DBSession.add(self.hosteditors)
        DBSession.flush()        

        self.hostmanagers = Group(name=u'hostmanagers', parent=self.hosteditors)
        DBSession.add(self.hostmanagers)
        DBSession.flush()

        # L'attribution des permissions.
        manage_perm = Permission.by_permission_name(u'manage')
        edit_perm = Permission.by_permission_name(u'edit')

        manage_perm.groups.append(self.hostmanagers)
        edit_perm.groups.append(self.hosteditors)
        DBSession.flush()
        transaction.commit()


    def tearDown(self):
        # This operation is only necessary for DBMS which are
        # really strict about table locks, such as PostgreSQL.
        # For our tests, we use an (in-memory) SQLite database,
        # so we're unaffected. This is done only for completeness.
        DBSession.delete(self.hostmanagers)
        DBSession.flush()
        transaction.commit()

        DBSession.delete(self.hosteditors)
        DBSession.flush()
        transaction.commit()
        TestController.tearDown(self)


    def test_groups_inheritance(self):
        """
        S'assure que les groupes sont correctement hérités.
        """

        # On obtient les variables de session comme si on était loggué
        # en tant que manager.
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get('/', extra_environ=environ)
        
        # On récupère la liste des groups auxquels l'utilisateur appartient.
        username = response.request.environ \
            ['repoze.who.identity'] \
            ['repoze.who.userid']
        grp = User.by_user_name(username).groups

        # On vérifie que la liste est correcte : le manager doit avoir accès
        # aux groupes 'hostmanagers' & 'hosteditors' (dont il hérite).
        assert_true( u'hostmanagers' in grp and u'hosteditors' in grp ,
            msg = "il est dans %s" % grp)

        # On recommence avec l'utilisateur editor.
        environ = {'REMOTE_USER': 'editor'}
        response = self.app.get('/', extra_environ=environ)

        username = response.request.environ \
            ['repoze.who.identity'] \
            ['repoze.who.userid']
        grp = User.by_user_name(username).groups

        # L'utilisateur editor ne doit avoir accès qu'au groupe 'hosteditors'.
        assert_true( not(u'hostmanagers' in grp) and u'hosteditors' in grp,
            msg = "il est dans %s" % grp)


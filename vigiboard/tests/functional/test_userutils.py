# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Test de la classe User Utils
"""
from nose.tools import assert_true

from vigiboard.model import DBSession, Group, Permission
from vigiboard.tests import TestController
from vigiboard.tests import teardown_db
import tg
import transaction
from nose.plugins.skip import SkipTest

class TestUserUtils(TestController):
    """Test retrieval of groups of hosts/services."""

    def test_get_user_groups(self):
        """
        Manager est dans le group hostmanagers et hosteditors
        et Editor seulement dans hosteditors
        """

#        # XXX This test has some issues, skip it until it gets fixed.
        raise SkipTest
#        
        # On commence par peupler la base
        hostmanagers = Group(name=u'hostmanagers', parent=None)
        DBSession.add(hostmanagers)

        hosteditors = Group(name=u'hosteditors', parent=hostmanagers)
        DBSession.add(hosteditors)

        manage_perm = Permission.by_permission_name(u'manage')
        edit_perm = Permission.by_permission_name(u'edit')

        manage_perm.groups.append(hostmanagers)
        edit_perm.groups.append(hosteditors)
        DBSession.flush()
        transaction.commit()
        
        # On obtient les variables de sessions comme si on était loggué
        # en tant que manager

        environ = {'REMOTE_USER': u'manager'}
        response = self.app.get('/', extra_environ=environ)
        
        # On récupère la liste des groups auquel on appartient
        
        user = response.request.environ.get('repoze.who.identity')
        grp = user.groups()
        print grp
        # On vérifie que la liste est correcte (vérifie la gestion des
        # groupes sous forme d'arbre)

        assert_true( u'hostmanagers' in grp and u'hosteditors' in grp ,
            msg = "il est dans %s" % grp)

        # On recommence pour l'utilisateur editor
        
        environ = {'REMOTE_USER': u'editor'}
        response = self.app.get('/', extra_environ=environ)
        
        user = response.request.environ.get('repoze.who.identity')
        grp = user.groups()
        
        assert_true( not(u'hostmanagers' in grp) and u'hosteditors' in grp,
            msg = "il est dans %s" % grp)


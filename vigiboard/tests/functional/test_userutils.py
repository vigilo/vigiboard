# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Teste l'héritage des permissions sur les groupes d'hôtes/services.
"""
import transaction
from nose.tools import assert_true

from vigilo.models.session import DBSession
from vigilo.models.tables import SupItemGroup, Permission, User, GroupHierarchy
from vigiboard.tests import TestController

class TestGroupPermissionsInheritance(TestController):
    """Test retrieval of groups of hosts/services."""
    def test_groups_inheritance(self):
        """
        S'assure que les groupes sont correctement hérités.
        """

        # Création de 2 groupes d'utilisateurs.
        hosteditors = SupItemGroup(name=u'hosteditors')
        DBSession.add(hosteditors)

        hostmanagers = SupItemGroup(name=u'hostmanagers')
        DBSession.add(hostmanagers)

        # Hiérarchie des groupes.
        DBSession.add(GroupHierarchy(
            parent=hosteditors,
            child=hosteditors,
            hops=0,
        ))
        DBSession.add(GroupHierarchy(
            parent=hostmanagers,
            child=hostmanagers,
            hops=0,
        ))
        DBSession.add(GroupHierarchy(
            parent=hostmanagers,
            child=hosteditors,
            hops=1,
        ))

        # L'attribution des permissions.
        manage_perm = Permission.by_permission_name(u'manage')
        edit_perm = Permission.by_permission_name(u'edit')

        manage_perm.supitemgroups.append(hostmanagers)
        edit_perm.supitemgroups.append(hosteditors)
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
        grp = User.by_user_name(username).supitemgroups()

        # Permet de rafraîchir les instances.
        hostmanagers = DBSession.query(SupItemGroup).filter(
                            SupItemGroup.name==u'hostmanagers').one()
        hosteditors = DBSession.query(SupItemGroup).filter(
                            SupItemGroup.name==u'hosteditors').one()

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
        grp = User.by_user_name(username).supitemgroups(False)

        # L'utilisateur editor ne doit avoir accès qu'au groupe 'hosteditors'.
        assert_true(not(hostmanagers.idgroup in grp) and
            hosteditors.idgroup in grp,
            msg = "il est dans %s" % grp)


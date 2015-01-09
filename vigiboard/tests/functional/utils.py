# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2015 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Fonctions utilitaires réutilisables dans les différents tests.
"""

import transaction

from vigilo.models.session import DBSession
from vigilo.models.demo import functions
from vigilo.models.tables import DataPermission, Permission, \
                            User, UserGroup


def populate_DB():
    """ Peuple la base de données. """

    # Création des 4 groupes de supitems :
    # - 1 groupe racine 'root' ;
    root = functions.add_supitemgroup(u'root')
    # - 1 groupe principal 'maingroup' ;
    maingroup = functions.add_supitemgroup(u'maingroup', root)
    # - 2 sous-groupes 'group1' et 'group2', faisant tous
    #   les deux parties du groupe principal 'maingroup'.
    group1 = functions.add_supitemgroup(u'group1', maingroup)
    group2 = functions.add_supitemgroup(u'group2', maingroup)

    # Création de 2 groupes d'utilisateurs (contenant chacun un utilisateur) :
    vigiboard_perm = Permission.by_permission_name(u'vigiboard-access')
    # - le premier avec des droits étendus
    #   (il a indirectement accès à tous les groupes de supitems) ;
    usergroup = UserGroup(group_name=u'users_with_access')
    usergroup.permissions.append(vigiboard_perm)
    DBSession.add(DataPermission(
        group = root,
        usergroup = usergroup,
        access = u'r',
    ))
    user = User(
        user_name=u'access',
        fullname=u'',
        email=u'user.has@access',
    )
    user.usergroups.append(usergroup)
    DBSession.add(user)

    # - le second avec des droits plus restreints
    #   (il n'a accès qu'au groupe de supitems 'group1').
    usergroup = UserGroup(group_name=u'users_with_limited_access')
    usergroup.permissions.append(vigiboard_perm)
    DBSession.add(DataPermission(
        group = group1,
        usergroup = usergroup,
        access = u'r',
    ))
    user = User(
        user_name=u'limited_access',
        fullname=u'',
        email=u'user.has.limited@access',
    )
    user.usergroups.append(usergroup)
    DBSession.add(user)
    DBSession.flush()

    # Création de 3 hôtes (1 par groupe de supitems).
    maingroup_host = functions.add_host(u'maingroup_host')
    group1_host = functions.add_host(u'group1_host')
    group2_host = functions.add_host(u'group2_host')

    # Affectation des hôtes aux groupes.
    maingroup.supitems.append(maingroup_host)
    group1.supitems.append(group1_host)
    group2.supitems.append(group2_host)
    DBSession.flush()

    # Création de 3 services de bas niveau (1 par hôte).
    group1_service = functions.add_lowlevelservice(
        group1_host, u'group1_service')
    group2_service = functions.add_lowlevelservice(
        group2_host, u'group2_service')
    maingroup_service = functions.add_lowlevelservice(
        maingroup_host, u'maingroup_service')

    # Ajout de 6 événements (1 par supitem)
    event1 = functions.add_event(maingroup_host, u'WARNING', u'foo')
    event2 = functions.add_event(maingroup_service, u'WARNING', u'foo')
    event3 = functions.add_event(group1_host, u'WARNING', u'foo')
    event4 = functions.add_event(group1_service, u'WARNING', u'foo')
    event5 = functions.add_event(group2_host, u'WARNING', u'foo')
    event6 = functions.add_event(group2_service, u'WARNING', u'foo')

    # Ajout de 5 événements corrélés (1 pour chaque évènement,
    # sauf celui touchant le 'maingroup_service' qui sera rattaché
    # à l'évènement corrélé causé par le 'maingroup_host').
    functions.add_correvent([event1, event2])
    functions.add_correvent([event3])
    functions.add_correvent([event4])
    functions.add_correvent([event5])
    functions.add_correvent([event6])
    transaction.commit()

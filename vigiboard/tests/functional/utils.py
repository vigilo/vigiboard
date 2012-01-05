# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2011 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Fonctions utilitaires réutilisables dans les différents tests.
"""

from nose.tools import assert_true, assert_equal
from datetime import datetime
import transaction

from vigilo.models.session import DBSession
from vigilo.models.tables import Event, CorrEvent, DataPermission, \
                            Permission, StateName, Host, SupItemGroup, \
                            LowLevelService, User, UserGroup, Permission
from vigiboard.tests import TestController

def populate_DB():
    """ Peuple la base de données. """

    # Création des 4 groupes de supitems :
    # - 1 groupe racine 'root' ;
    root = SupItemGroup(name=u'root', parent=None)
    DBSession.add(root)
    # - 1 groupe principal 'maingroup' ;
    maingroup = SupItemGroup(name=u'maingroup', parent=root)
    DBSession.add(maingroup)
    # - 2 sous-groupes 'group1' et 'group2', faisant tous
    #   les deux parties du groupe principal 'maingroup'.
    group1 = SupItemGroup(name=u'group1', parent=maingroup)
    DBSession.add(group1)
    group2 = SupItemGroup(name=u'group2', parent=maingroup)
    DBSession.add(group2)
    DBSession.flush()

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
    host_template = {
        'checkhostcmd': u'halt',
        'snmpcommunity': u'public',
        'hosttpl': u'/dev/null',
        'address': u'192.168.1.1',
        'snmpport': 42,
        'weight': 42,
    }

    maingroup_host = Host(name=u'maingroup_host', **host_template)
    DBSession.add(maingroup_host)
    group1_host = Host(name=u'group1_host', **host_template)
    DBSession.add(group1_host)
    group2_host = Host(name=u'group2_host', **host_template)
    DBSession.add(group2_host)

    # Affectation des hôtes aux groupes.
    maingroup.supitems.append(maingroup_host)
    group1.supitems.append(group1_host)
    group2.supitems.append(group2_host)
    DBSession.flush()

    # Création de 3 services de bas niveau (1 par hôte).
    service_template = {
        'command': u'halt',
        'weight': 42,
    }

    group1_service = LowLevelService(
        host = group1_host,
        servicename = u'group1_service',
        **service_template
    )
    DBSession.add(group1_service)

    group2_service = LowLevelService(
        host = group2_host,
        servicename = u'group2_service',
        **service_template
    )
    DBSession.add(group2_service)

    maingroup_service = LowLevelService(
        host = maingroup_host,
        servicename = u'maingroup_service',
        **service_template
    )
    DBSession.add(maingroup_service)
    DBSession.flush()

    # Ajout de 6 événements (1 par supitem)
    event_template = {
        'message': u'foo',
        'current_state': StateName.statename_to_value(u'WARNING'),
        'timestamp': datetime.now(),
    }

    event1 = Event(supitem=maingroup_host, **event_template)
    DBSession.add(event1)
    event2 = Event(supitem=maingroup_service, **event_template)
    DBSession.add(event2)
    event3 = Event(supitem=group1_host, **event_template)
    DBSession.add(event3)
    event4 = Event(supitem=group1_service, **event_template)
    DBSession.add(event4)
    event5 = Event(supitem=group2_host, **event_template)
    DBSession.add(event5)
    event6 = Event(supitem=group2_service, **event_template)
    DBSession.add(event6)
    DBSession.flush()

    # Ajout de 5 événements corrélés (1 pour chaque évènement,
    # sauf celui touchant le 'maingroup_service' qui sera rattaché
    # à l'évènement corrélé causé par le 'maingroup_host').
    aggregate_template = {
        'timestamp_active': datetime.now(),
        'priority': 1,
        'ack': CorrEvent.ACK_NONE,
    }

    aggregate1 = CorrEvent(
        idcause=event1.idevent, **aggregate_template)
    aggregate3 = CorrEvent(
        idcause=event3.idevent, **aggregate_template)
    aggregate4 = CorrEvent(
        idcause=event4.idevent, **aggregate_template)
    aggregate5 = CorrEvent(
        idcause=event5.idevent, **aggregate_template)
    aggregate6 = CorrEvent(
        idcause=event6.idevent, **aggregate_template)

    aggregate1.events.append(event1)
    aggregate1.events.append(event2)
    aggregate3.events.append(event3)
    aggregate4.events.append(event4)
    aggregate5.events.append(event5)
    aggregate6.events.append(event6)
    DBSession.add(aggregate1)
    DBSession.add(aggregate3)
    DBSession.add(aggregate4)
    DBSession.add(aggregate5)
    DBSession.add(aggregate6)
    DBSession.flush()

    transaction.commit()

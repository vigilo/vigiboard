# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Test du tableau d'événements de Vigiboard
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
    # On ajoute les groupes et leurs dépendances
    hostmanagers = SupItemGroup(name=u'managersgroup')
    DBSession.add(hostmanagers)
    hosteditors = SupItemGroup(name=u'editorsgroup', parent=hostmanagers)
    DBSession.add(hosteditors)
    DBSession.flush()

    usergroup = UserGroup.by_group_name(u'users_with_access')
    DBSession.add(DataPermission(
        group=hostmanagers,
        usergroup=usergroup,
        access=u'r',
    ))
    DBSession.add(DataPermission(
        group=hosteditors,
        usergroup=usergroup,
        access=u'r',
    ))

    usergroup = UserGroup.by_group_name(u'users_with_limited_access')
    DBSession.add(DataPermission(
        group=hosteditors,
        usergroup=usergroup,
        access=u'r',
    ))
    DBSession.flush()

    # Création des hôtes de test.
    host_template = {
        'checkhostcmd': u'halt',
        'snmpcommunity': u'public',
        'hosttpl': u'/dev/null',
        'address': u'192.168.1.1',
        'snmpport': 42,
        'weight': 42,
    }

    managerhost = Host(name=u'managerhost', **host_template)
    editorhost = Host(name=u'editorhost', **host_template)
    DBSession.add(managerhost)
    DBSession.add(editorhost)

    # Affectation des hôtes aux groupes.
    hosteditors.supitems.append(editorhost)
    hostmanagers.supitems.append(managerhost)
    DBSession.flush()

    # Création des services techniques de test.
    service_template = {
        'command': u'halt',
        'op_dep': u'+',
        'weight': 42,
    }

    service1 = LowLevelService(
        host=managerhost,
        servicename=u'managerservice',
        **service_template
    )

    service2 = LowLevelService(
        host=editorhost,
        servicename=u'managerservice',
        **service_template
    )

    service3 = LowLevelService(
        host=managerhost,
        servicename=u'editorservice',
        **service_template
    )

    service4 = LowLevelService(
        host=editorhost,
        servicename=u'editorservice',
        **service_template
    )

    DBSession.add(service1)
    DBSession.add(service2)
    DBSession.add(service3)
    DBSession.add(service4)
    DBSession.flush()

    # Ajout des événements eux-mêmes
    event_template = {
        'message': u'foo',
        'current_state': StateName.statename_to_value(u'WARNING'),
        'timestamp': datetime.now(),
    }

    event1 = Event(supitem=service1, **event_template)
    event2 = Event(supitem=service2, **event_template)
    event3 = Event(supitem=service3, **event_template)
    event4 = Event(supitem=service4, **event_template)
    event5 = Event(supitem=editorhost, **event_template)
    event6 = Event(supitem=managerhost, **event_template)

    DBSession.add(event1)
    DBSession.add(event2)
    DBSession.add(event3)
    DBSession.add(event4)
    DBSession.add(event5)
    DBSession.add(event6)
    DBSession.flush()

    # Ajout des événements corrélés
    aggregate_template = {
        'timestamp_active': datetime.now(),
        'priority': 1,
        'status': u'None',
    }

    aggregate1 = CorrEvent(
        idcause=event1.idevent, **aggregate_template)
    aggregate2 = CorrEvent(
        idcause=event4.idevent, **aggregate_template)
    aggregate3 = CorrEvent(
        idcause=event5.idevent, **aggregate_template)
    aggregate4 = CorrEvent(
        idcause=event6.idevent, **aggregate_template)

    aggregate1.events.append(event1)
    aggregate1.events.append(event3)
    aggregate2.events.append(event4)
    aggregate2.events.append(event2)
    aggregate3.events.append(event5)
    aggregate4.events.append(event6)
    DBSession.add(aggregate1)
    DBSession.add(aggregate2)
    DBSession.add(aggregate3)
    DBSession.add(aggregate4)

    DBSession.flush()
    transaction.commit()

class TestEventTable(TestController):
    """
    Test du tableau d'événements de Vigiboard
    """
    def setUp(self):
        super(TestEventTable, self).setUp()
        perm = Permission.by_permission_name(u'vigiboard-access')

        user = User(
            user_name=u'access',
            fullname=u'',
            email=u'user.has@access',
        )
        usergroup = UserGroup(
            group_name=u'users_with_access',
        )
        usergroup.permissions.append(perm)
        user.usergroups.append(usergroup)
        DBSession.add(user)
        DBSession.add(usergroup)
        DBSession.flush()

        user = User(
            user_name=u'limited_access',
            fullname=u'',
            email=u'user.has.no@access',
        )
        usergroup = UserGroup(
            group_name=u'users_with_limited_access',
        )
        usergroup.permissions.append(perm)
        user.usergroups.append(usergroup)
        DBSession.add(user)
        DBSession.add(usergroup)
        DBSession.flush()

        populate_DB()


    def test_homepage(self):
        """
        Tableau des événements (page d'accueil).
        """
        # L'utilisateur n'est pas authentifié.
        response = self.app.get('/', status=401)

        # L'utilisateur est authentifié avec des permissions réduites.
        environ = {'REMOTE_USER': 'limited_access'}
        response = self.app.get('/', extra_environ=environ)

        # Il doit y avoir 2 lignes de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 2)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

        # L'utilisateur est authentifié avec des permissions plus étendues.
        environ = {'REMOTE_USER': 'access'}
        response = self.app.get('/', extra_environ=environ)

        # Il doit y avoir 4 lignes de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 4)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

    def test_correvents_table_for_LLS(self):
        """
        Tableau des événements corrélés pour un service de bas niveau.
        """
        url = '/item/1/%s/%s' % ('managerhost', 'managerservice')

        # L'utilisateur n'est pas authentifié.
        response = self.app.get(url, status=401)

        # L'utilisateur dispose de permissions restreintes.
        # Il n'a pas accès aux événements corrélés sur le service donné.
        # Donc, on s'attend à être redirigé avec un message d'erreur.
        environ = {'REMOTE_USER': 'limited_access'}
        response = self.app.get(url, extra_environ=environ, status=302)
        response = response.follow(status = 200, extra_environ = environ)
        assert_true(len(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]')))

        # L'utilisateur dispose de permissions plus étendues.
        # Il doit avoir accès à l'historique.
        # Ici, il n'y a qu'un seul événement corrélé pour ce service.
        environ = {'REMOTE_USER': 'access'}
        response = self.app.get(url, extra_environ=environ, status=200)

        # Il doit y avoir 1 ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

    def test_correvents_table_for_host(self):
        """
        Tableau des événements corrélés pour un hôte.
        """
        url = '/item/1/%s/' % ('managerhost', )

        # L'utilisateur n'est pas authentifié.
        response = self.app.get(url, status=401)

        # L'utilisateur dispose de permissions restreintes.
        # Il n'a pas accès aux événements corrélés sur le service donné.
        # Donc, on s'attend à être redirigé avec un message d'erreur.
        environ = {'REMOTE_USER': 'limited_access'}
        response = self.app.get(url, extra_environ=environ, status=302)
        response = response.follow(status = 200, extra_environ = environ)
        assert_true(len(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]')))

        # L'utilisateur dispose de permissions plus étendues.
        # Il doit avoir accès à l'historique.
        # Ici, il n'y a qu'un seul événement corrélé pour ce service.
        environ = {'REMOTE_USER': 'access'}
        response = self.app.get(url, extra_environ=environ, status=200)

        # Il doit y avoir 1 ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)


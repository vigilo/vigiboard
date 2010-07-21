# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Test du tableau d'événements de Vigiboard
"""

from nose.tools import assert_true, assert_equal
from datetime import datetime
import transaction

from vigilo.models.session import DBSession
from vigilo.models.tables import Event, EventHistory, CorrEvent, User, \
                            Permission, StateName, Host, UserGroup, \
                            LowLevelService, SupItemGroup, DataPermission
from vigiboard.tests import TestController

def populate_accounts():
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
        transaction.commit()

def populate_DB(caused_by_service):
    """ Peuple la base de données. """
    # On ajoute un groupe d'hôtes et un groupe de services.
    supitemmanagers = SupItemGroup(name = u'managersgroup')
    DBSession.add(supitemmanagers)
    DBSession.flush()

    usergroup = UserGroup.by_group_name(u'users_with_access')
    DBSession.add(DataPermission(
        group=supitemmanagers,
        usergroup=usergroup,
        access=u'r',
    ))
    DBSession.flush()

    # On crée un hôte de test, et on l'ajoute au groupe d'hôtes.
    managerhost = Host(
        name = u'managerhost',      
        checkhostcmd = u'halt',
        snmpcommunity = u'public',
        hosttpl = u'/dev/null',
        address = u'192.168.1.1',
        snmpport = 42,
        weight = 42,
    )
    DBSession.add(managerhost)
    supitemmanagers.supitems.append(managerhost)
    DBSession.flush()

    # On crée un services de bas niveau, et on l'ajoute au groupe de services.
    managerservice = LowLevelService(
        host = managerhost,
        servicename = u'managerservice',
        command = u'halt',
        op_dep = u'+',
        weight = 42,
    )
    DBSession.add(managerservice)
    supitemmanagers.supitems.append(managerservice)
    DBSession.flush()

    if caused_by_service:
        supitem = managerservice
    else:
        supitem = managerhost

    # Ajout d'un événement
    event = Event(
        supitem = supitem, 
        message = u'foo',
        current_state = StateName.statename_to_value(u"WARNING"),
        timestamp = datetime.now(),
    )
    DBSession.add(event)
    DBSession.flush()

    # Ajout des historiques
    DBSession.add(EventHistory(
        type_action=u'Nagios update state',
        idevent=event.idevent, 
        timestamp=datetime.now()))
    DBSession.add(EventHistory(
        type_action=u'Acknowlegement change state',
        idevent=event.idevent, 
        timestamp=datetime.now()))
    DBSession.flush()

    # Ajout d'un événement corrélé
    aggregate = CorrEvent(
        idcause = event.idevent, 
        timestamp_active = datetime.now(),
        priority = 1,
        status = u"None")
    aggregate.events.append(event)
    DBSession.add(aggregate)
    DBSession.flush()
    return aggregate.idcorrevent

def add_masked_event(idcorrevent):
    """Ajoute un événement masqué à un événement corrélé."""
    transaction.begin()
    hostmanagers = SupItemGroup.by_group_name(u'managersgroup')
    nb_hosts = DBSession.query(Host).count()

    masked_host = Host(
        name = u'masked host #%d' % nb_hosts,      
        checkhostcmd = u'halt',
        snmpcommunity = u'public',
        hosttpl = u'/dev/null',
        address = u'192.168.1.%d' % nb_hosts,
        snmpport = 42,
        weight = 42,
    )
    DBSession.add(masked_host)
    hostmanagers.supitems.append(masked_host)
    DBSession.flush()

    event = Event(
        supitem = masked_host,
        message = u'masked event #%d' % nb_hosts,
        current_state = StateName.statename_to_value(u"CRITICAL"),
        timestamp = datetime.now(),
    )
    DBSession.add(event)
    DBSession.flush()

    aggregate = DBSession.query(CorrEvent).filter(
        CorrEvent.idcorrevent == idcorrevent).one()
    aggregate.events.append(event)
    DBSession.add(aggregate)
    DBSession.flush()
    transaction.commit()


class TestRawEventsTableAnonymousLLS(TestController):
    """
    Teste l'affichage des événements bruts masqués par un agrégat.
    Dans ces tests, l'utilisateur n'est pas authentifié et l'agrégat
    a été causé par un LLS.
    """
    test_service = True

    def setUp(self):
        super(TestRawEventsTableAnonymousLLS, self).setUp()
        populate_accounts()

    def test_table(self):
        """Événements masqués d'un agrégat sur un LLS en anonyme."""
        # On peuple la BDD avec un hôte, un service de bas niveau,
        # et un groupe d'hôtes et de services associés à ces items.
        idcorrevent = populate_DB(self.test_service)
        transaction.commit()

        # L'utilisateur n'est pas authentifié.
        # On s'attend à ce qu'une erreur 401 soit renvoyée,
        # demandant à l'utilisateur de s'authentifier.
        response = self.app.get(
            '/masked_events/%d' % idcorrevent,
            status = 401)

class TestRawEventsTableAnonymousHost(TestRawEventsTableAnonymousLLS):
    """Idem que TestRawEventsTableAnonymousLLS mais avec un hôte."""
    test_service = False

    def test_table(self):
        """Événements masqués d'un agrégat sur un hôte en anonyme."""
        super(TestRawEventsTableAnonymousHost, self).test_table()


class TestRawEventsTableWithoutPermsLLS(TestController):
    """
    Teste l'affichage des événements bruts masqués par un agrégat.
    Dans ces tests, l'utilisateur n'a pas les bonnes permissions
    et l'agrégat a été causé par un LLS.
    """
    test_service = True

    def setUp(self):
        super(TestRawEventsTableWithoutPermsLLS, self).setUp()
        populate_accounts()

    def test_table(self):
        """Événements masqués d'un agrégat sur un LLS sans permissions."""
        # On peuple la BDD avec un hôte, un service de bas niveau,
        # et un groupe d'hôtes et de services associés à ces items.
        idcorrevent = populate_DB(self.test_service)
        transaction.commit()

        environ = {'REMOTE_USER': 'limited_access'}

        # On s'attend à ce qu'une erreur 302 soit renvoyée, et à
        # ce qu'un message d'erreur précise à l'utilisateur qu'il
        # n'a pas accès aux informations concernant cet évènement.
        response = self.app.get(
            '/masked_events/%d' % idcorrevent,
            status = 302, 
            extra_environ = environ)
        response = response.follow(status = 200, extra_environ = environ)
        assert_true(len(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]')))

        # L'erreur 302 peut venir de l'absence de permissions
        # ou bien simplement de l'absence d'événements masqués.
        # Pour vérifier qu'il s'agit bien d'un problème de permissions,
        # on ajoute un événement masqué. On doit à nouveau obtenir
        # une erreur 302.
        add_masked_event(idcorrevent)
        response = self.app.get(
            '/masked_events/%d' % idcorrevent,
            status = 302, 
            extra_environ = environ)
        response = response.follow(status = 200, extra_environ = environ)
        assert_true(len(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]')))

class TestRawEventsTableWithoutPermsHost(TestRawEventsTableWithoutPermsLLS):
    """Idem que TestRawEventsTableWithoutPermsLLS mais avec un hôte."""
    test_service = False

    def test_table(self):
        """Événements masqués d'un agrégat sur un hôte sans permissions."""
        super(TestRawEventsTableWithoutPermsHost, self).test_table()

class TestRawEventsTableWithPermsLLS(TestController):
    """
    Teste l'affichage d'une table des événements bruts
    rattachés à un agrégat, hormis la cause de cet agrégat.
    """
    test_service = True

    def setUp(self):
        super(TestRawEventsTableWithPermsLLS, self).setUp()
        populate_accounts()

    def test_table(self):
        """Événements masqués d'un agrégat sur un LLS avec permissions."""
        # On peuple la BDD avec un hôte, un service de bas niveau,
        # et un groupe d'hôtes et de services associés à ces items.
        idcorrevent = populate_DB(True)
        transaction.commit()

        environ = {'REMOTE_USER': 'access'}

        # On s'attend à ce qu'une erreur 302 soit renvoyée, et à
        # ce qu'un message d'erreur précise à l'utilisateur qu'il
        # n'a pas accès aux informations concernant cet évènement.
        response = self.app.get(
            '/masked_events/%d' % idcorrevent,
            status = 302,
            extra_environ = environ)
        response = response.follow(status = 200, extra_environ = environ)
        assert_true(len(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]')))

        # L'erreur 302 peut venir de l'absence de permissions
        # ou bien simplement de l'absence d'événements masqués.
        # Pour vérifier qu'il s'agit bien d'un problème de permissions,
        # on ajoute un événement masqué. On doit avoir accès à exactement
        # 1 événement masqué à présent.
        add_masked_event(idcorrevent)
        response = self.app.get(
            '/masked_events/%d' % idcorrevent,
            status = 200,
            extra_environ = environ)

        # On s'attend à trouver exactement 1 événement masqué.
        # NB: la requête XPath est approchante, car XPath 1.0 ne permet pas
        # de rechercher directement une valeur dans une liste. Elle devrait
        # néanmoins suffire pour les besoins des tests.
        rows = response.lxml.xpath(
            '//table[contains(@class, "vigitable")]/tbody/tr')
        assert_equal(len(rows), 1)

class TestRawEventsTableWithPermsHost(TestRawEventsTableWithPermsLLS):
    """Idem que TestRawEventsTableWithPermsLLS mais avec un hôte."""
    test_service = False

    def test_table(self):
        """Événements masqués d'un agrégat sur un hôte avec permissions."""
        super(TestRawEventsTableWithPermsHost, self).test_table()


# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Vérifie que la page qui affiche l'historique des actions sur un événement
brut fonctionne correctement.
"""

from nose.tools import assert_true, assert_equal
from datetime import datetime
import transaction

from vigilo.models.session import DBSession
from vigilo.models.tables import Event, EventHistory, CorrEvent, \
                            Permission, StateName, Host, \
                            SupItemGroup, LowLevelService, \
                            Permission, DataPermission, User, \
                            UserGroup
from vigiboard.tests import TestController

def populate_DB():
    """ Peuple la base de données. """
    # On ajoute un groupe d'hôtes et un groupe de services.
    supitemmanagers = SupItemGroup(name=u'managersgroup')
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
        weight = 42,
    )
    DBSession.add(managerservice)
    supitemmanagers.supitems.append(managerservice)
    DBSession.flush()
    
    return (managerhost, managerservice)

def add_correvent_caused_by(supitem):
    """
    Ajoute dans la base de données un évènement corrélé causé 
    par un incident survenu sur l'item passé en paramètre.
    Génère un historique pour les tests.
    """

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
    
    return event.idevent
    

class TestHistoryTable(TestController):
    """
    Teste la table qui affiche l'historique des actions
    sur un événement brut.
    """
    def setUp(self):
        super(TestHistoryTable, self).setUp()
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


    def test_cause_host_history(self):
        """Historique de la cause d'un événement corrélé sur un hôte."""

        # On peuple la BDD avec un hôte, un service de bas niveau,
        # et un groupe d'hôtes et de services associés à ces items.
        (managerhost, managerservice) = populate_DB()
        
        # On ajoute un évènement corrélé causé par l'hôte
        idevent = add_correvent_caused_by(managerhost)
        transaction.commit()

        # L'utilisateur n'est pas authentifié.
        # On s'attend à ce qu'une erreur 401 soit renvoyée,
        # demandant à l'utilisateur de s'authentifier.
        response = self.app.get(
            '/event/%d' % idevent,
            status = 401)

        # L'utilisateur N'A PAS les bonnes permissions.
        environ = {'REMOTE_USER': 'limited_access'}
        
        # On s'attend à ce qu'une erreur 302 soit renvoyée, et à
        # ce qu'un message d'erreur précise à l'utilisateur qu'il
        # n'a pas accès aux informations concernant cet évènement.
        response = self.app.get(
            '/event/%d' % idevent,
            status = 302, 
            extra_environ = environ)

        # On suit la redirection.
        response = response.follow(status = 200, extra_environ = environ)
        assert_true(len(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]')))

        # L'utilisateur a les bonnes permissions.
        environ = {'REMOTE_USER': 'access'}
        
        # On s'attend à ce que le statut de la requête soit 200.
        response = self.app.get(
            '/event/%d' % idevent,
            status = 200, 
            extra_environ = environ)

        # Il doit y avoir 2 lignes de résultats.
        # NB: la requête XPath est approchante, car XPath 1.0 ne permet pas
        # de rechercher directement une valeur dans une liste. Elle devrait
        # néanmoins suffire pour les besoins des tests.
        rows = response.lxml.xpath(
            '//table[contains(@class, "vigitable")]/tbody/tr')
        assert_equal(len(rows), 2)

    def test_cause_service_history(self):
        """Historique de la cause d'un événement corrélé sur un LLS."""

        # On peuple la BDD avec un hôte, un service de bas niveau,
        # et un groupe d'hôtes et de services associés à ces items.
        (managerhost, managerservice) = populate_DB()
        
        # On ajoute un évènement corrélé causé par le service
        idevent = add_correvent_caused_by(managerservice)
        
        transaction.commit()

        # L'utilisateur n'est pas authentifié.
        # On s'attend à ce qu'une erreur 401 soit renvoyée,
        # demandant à l'utilisateur de s'authentifier.
        response = self.app.get(
            '/event/%d' % idevent,
            status = 401)

        # L'utilisateur N'A PAS les bonnes permissions.
        environ = {'REMOTE_USER': 'limited_access'}
        
        # On s'attend à ce qu'une erreur 302 soit renvoyée, et à
        # ce qu'un message d'erreur précise à l'utilisateur qu'il
        # n'a pas accès aux informations concernant cet évènement.
        response = self.app.get(
            '/event/%d' % idevent,
            status = 302, 
            extra_environ = environ)

        # On suit la redirection.
        response = response.follow(status = 200, extra_environ = environ)
        assert_true(len(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]')))

        # L'utilisateur a les bonnes permissions.
        environ = {'REMOTE_USER': 'access'}
        
        # On s'attend à ce que le statut de la requête soit 200.
        response = self.app.get(
            '/event/%d' % idevent,
            status = 200, 
            extra_environ = environ)

        # Il doit y avoir 2 lignes de résultats.
        # NB: la requête XPath est approchante, car XPath 1.0 ne permet pas
        # de rechercher directement une valeur dans une liste. Elle devrait
        # néanmoins suffire pour les besoins des tests.
        rows = response.lxml.xpath(
            '//table[contains(@class,"vigitable")]/tbody/tr')
        assert_equal(len(rows), 2)


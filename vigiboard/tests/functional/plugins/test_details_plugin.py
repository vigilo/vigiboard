# -*- coding: utf-8 -*-
"""
Teste le formulaire donnant les liens vers les outils extérieurs
et les données de l'historique.
"""
from nose.tools import assert_true, assert_equal
from datetime import datetime
import transaction

from vigiboard.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.tables import User, UserGroup, \
                            Permission, DataPermission, StateName, \
                            LowLevelService, Event, CorrEvent, Host
from vigilo.models.demo.functions import *

def insert_deps(return_service):
    """
    Insère les dépendances nécessaires aux tests.

    @param return_service: Indique si les événements générés
        concernent un hôte (False) ou un service de bas niveau (True).
    @type return_service: C{bool}
    @return: Renvoie un tuple avec le groupe d'hôte créé,
        l'identifiant du L{CorrEvent} généré et enfin,
        l'identifiant de l'L{Event} généré.
    @rtype: C{tuple}
    """
    timestamp = datetime.now()

    hostgroup = add_supitemgroup(name=u'foo')

    host = Host(
        name=u'bar',
        checkhostcmd=u'',
        description=u'',
        hosttpl=u'',
        address=u'127.0.0.1',
        snmpport=42,
        snmpcommunity=u'public',
        snmpversion=u'3',
        weight=42,
    )
    DBSession.add(host)
    DBSession.flush()

    hostgroup.supitems.append(host)
    DBSession.flush()

    servicegroup = add_supitemgroup(name=u'bar')

    service = LowLevelService(
        host=host,
        command=u'',
        weight=42,
        servicename=u'baz',
    )
    DBSession.add(service)
    DBSession.flush()

    servicegroup.supitems.append(service)
    DBSession.flush()

    event = Event(
        timestamp=timestamp,
        current_state=StateName.statename_to_value(u'WARNING'),
        message=u'Hello world',
    )
    if return_service:
        event.supitem = service
    else:
        event.supitem = host
    DBSession.add(event)
    DBSession.flush()

    correvent = CorrEvent(
        impact=42,
        priority=42,
        trouble_ticket=None,
        status=u'None',
        occurrence=42,
        timestamp_active=timestamp,
        cause=event,
    )
    correvent.events.append(event)
    DBSession.add(correvent)
    DBSession.flush()

    usergroup = UserGroup.by_group_name(u'users_with_access')
    DBSession.add(DataPermission(
        usergroup=usergroup,
        group=hostgroup,
        access=u'r',
    ))
    DBSession.flush()

    transaction.commit()
    correvent = DBSession.query(CorrEvent).first()
    event = DBSession.query(Event).first()

    return (hostgroup, correvent.idcorrevent, event.idevent)

class TestDetailsPlugin(TestController):
    """Teste le dialogue pour l'accès aux historiques."""
    def setUp(self):
        super(TestDetailsPlugin, self).setUp()
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
            user_name=u'no_access',
            fullname=u'',
            email=u'user.has.no@access',
        )
        usergroup = UserGroup(
            group_name=u'users_without_access',
        )
        usergroup.permissions.append(perm)
        user.usergroups.append(usergroup)
        DBSession.add(user)
        DBSession.add(usergroup)
        DBSession.flush()

        transaction.commit()

    def test_details_plugin_LLS_alert_when_allowed(self):
        """Dialogue des détails avec un LLS et les bons droits."""
        hostgroup, idcorrevent, idcause = insert_deps(True)

        response = self.app.post('/get_plugin_value', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, extra_environ={'REMOTE_USER': 'access'})
        json = response.json

        # Le contenu de "eventdetails" varie facilement.
        # On le teste séparément.
        json.pop('eventdetails', None)
        assert_true('eventdetails' in response.json)

        assert_equal(json, {
            "idcorrevent": idcorrevent,
            "idcause": idcause,
            "service": "baz",
            "peak_state": "WARNING",
            "current_state": "WARNING",
            "host": "bar",
            "initial_state": "WARNING"
        })

    def test_details_plugin_host_alert_when_allowed(self):
        """Dialogue des détails avec un hôte et les bons droits."""
        hostgroup, idcorrevent, idcause = insert_deps(False)

        response = self.app.post('/get_plugin_value', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, extra_environ={'REMOTE_USER': 'access'})
        json = response.json

        # Le contenu de "eventdetails" varie facilement.
        # On le teste séparément.
        json.pop('eventdetails', None)
        assert_true('eventdetails' in response.json)

        assert_equal(json, {
            "idcorrevent": idcorrevent,
            "idcause": idcause,
            "service": None,
            "peak_state": "WARNING",
            "current_state": "WARNING",
            "host": "bar",
            "initial_state": "WARNING"
        })


    def test_details_plugin_LLS_when_forbidden(self):
        """Dialogue des détails avec un LLS et des droits insuffisants."""
        idcorrevent = insert_deps(True)[1]

        # Le contrôleur renvoie une erreur 404 (HTTPNotFound)
        # lorsque l'utilisateur n'a pas les permissions nécessaires sur
        # les données ou qu'aucun événement correspondant n'est trouvé.
        self.app.post('/get_plugin_value', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, extra_environ={'REMOTE_USER': 'no_access'},
            status=404)

    def test_details_plugin_host_when_forbidden(self):
        """Dialogue des détails avec un hôte et des droits insuffisants."""
        idcorrevent = insert_deps(False)[1]

        # Le contrôleur renvoie une erreur 404 (HTTPNotFound)
        # lorsque l'utilisateur n'a pas les permissions nécessaires sur
        # les données ou qu'aucun événement correspondant n'est trouvé.
        self.app.post('/get_plugin_value', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, extra_environ={'REMOTE_USER': 'no_access'},
            status=404)

    def test_details_plugin_LLS_anonymous(self):
        """Dialogue des détails avec un LLS et en anonyme."""
        idcorrevent = insert_deps(True)[1]

        # Le contrôleur renvoie une erreur 401 (HTTPUnauthorized)
        # lorsque l'utilisateur n'est pas authentifié.
        self.app.post('/get_plugin_value', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, status=401)

    def test_details_plugin_host_anonymous(self):
        """Dialogue des détails avec un hôte et en anonyme."""
        idcorrevent = insert_deps(False)[1]

        # Le contrôleur renvoie une erreur 401 (HTTPUnauthorized)
        # lorsque l'utilisateur n'est pas authentifié.
        self.app.post('/get_plugin_value', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, status=401)

# -*- coding: utf-8 -*-
# Copyright (C) 2006-2019 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Teste le formulaire donnant les liens vers les outils extérieurs
et les données de l'historique.
"""
from nose.tools import assert_true, assert_equal
from datetime import datetime
import transaction

from vigiboard.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.demo import functions
from vigilo.models.tables import User, UserGroup, Event, CorrEvent, \
                            Permission, DataPermission

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

    hostgroup = functions.add_supitemgroup(u'foo')
    host = functions.add_host(u'bar')
    hostgroup.supitems.append(host)
    DBSession.flush()

    servicegroup = functions.add_supitemgroup(u'bar')
    service = functions.add_lowlevelservice(host, u'baz')
    servicegroup.supitems.append(service)
    DBSession.flush()

    if return_service:
        event = functions.add_event(service, u'WARNING', u'', timestamp)
    else:
        event = functions.add_event(host, u'WARNING', u'', timestamp)

    correvent = functions.add_correvent([event], timestamp=timestamp)

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
    return (correvent.idcorrevent, event.idevent)

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
        usergroup = UserGroup(group_name=u'users_with_access')
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
        usergroup = UserGroup(group_name=u'users_without_access')
        usergroup.permissions.append(perm)
        user.usergroups.append(usergroup)
        DBSession.add(user)
        DBSession.add(usergroup)
        DBSession.flush()

        transaction.commit()

    def test_details_plugin_LLS_alert_when_allowed(self):
        """Dialogue des détails avec un LLS et les bons droits."""
        idcorrevent, idcause = insert_deps(True)

        response = self.app.post('/plugin_json', {
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
            "initial_state": "WARNING",
            "maps": [],
        })

    def test_details_plugin_LLS_alert_when_manager(self):
        """Dialogue des détails avec un LLS en tant que manager."""
        idcorrevent, idcause = insert_deps(True)

        response = self.app.post('/plugin_json', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, extra_environ={'REMOTE_USER': 'manager'})
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
            "initial_state": "WARNING",
            "maps": [],
        })

    def test_details_plugin_host_alert_when_allowed(self):
        """Dialogue des détails avec un hôte et les bons droits."""
        idcorrevent, idcause = insert_deps(False)

        response = self.app.post('/plugin_json', {
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
            "initial_state": "WARNING",
            "maps": [],
        })

    def test_details_plugin_host_alert_when_manager(self):
        """Dialogue des détails avec un hôte en tant que manager."""
        idcorrevent, idcause = insert_deps(False)

        response = self.app.post('/plugin_json', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, extra_environ={'REMOTE_USER': 'manager'})
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
            "initial_state": "WARNING",
            "maps": [],
        })

    def test_details_plugin_LLS_when_forbidden(self):
        """Dialogue des détails avec un LLS et des droits insuffisants."""
        idcorrevent = insert_deps(True)[0]

        # Le contrôleur renvoie une erreur 404 (HTTPNotFound)
        # lorsque l'utilisateur n'a pas les permissions nécessaires sur
        # les données ou qu'aucun événement correspondant n'est trouvé.
        self.app.post('/plugin_json', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, extra_environ={'REMOTE_USER': 'no_access'},
            status=404)

    def test_details_plugin_host_when_forbidden(self):
        """Dialogue des détails avec un hôte et des droits insuffisants."""
        idcorrevent = insert_deps(False)[0]

        # Le contrôleur renvoie une erreur 404 (HTTPNotFound)
        # lorsque l'utilisateur n'a pas les permissions nécessaires sur
        # les données ou qu'aucun événement correspondant n'est trouvé.
        self.app.post('/plugin_json', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, extra_environ={'REMOTE_USER': 'no_access'},
            status=404)

    def test_details_plugin_LLS_anonymous(self):
        """Dialogue des détails avec un LLS et en anonyme."""
        idcorrevent = insert_deps(True)[0]

        # Le contrôleur renvoie une erreur 401 (HTTPUnauthorized)
        # lorsque l'utilisateur n'est pas authentifié.
        self.app.post('/plugin_json', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, status=401)

    def test_details_plugin_host_anonymous(self):
        """Dialogue des détails avec un hôte et en anonyme."""
        idcorrevent = insert_deps(False)[0]

        # Le contrôleur renvoie une erreur 401 (HTTPUnauthorized)
        # lorsque l'utilisateur n'est pas authentifié.
        self.app.post('/plugin_json', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, status=401)

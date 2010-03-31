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
from vigilo.models.tables import ServiceGroup, HostGroup, \
                            Host, Permission, StateName, \
                            LowLevelService, Event, CorrEvent

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

    hostgroup = HostGroup(
        name=u'foo',
    )
    DBSession.add(hostgroup)

    host = Host(
        name=u'bar',
        checkhostcmd=u'',
        description=u'',
        hosttpl=u'',
        mainip=u'127.0.0.1',
        snmpport=42,
        snmpcommunity=u'public',
        snmpversion=u'3',
        weight=42,
    )
    DBSession.add(host)
    DBSession.flush()

    hostgroup.hosts.append(host)
    DBSession.flush()

    servicegroup = ServiceGroup(
        name=u'foo',
    )
    DBSession.add(servicegroup)

    service = LowLevelService(
        host=host,
        command=u'',
        weight=42,
        servicename=u'baz',
        op_dep=u'&',
    )
    DBSession.add(service)
    DBSession.flush()

    servicegroup.services.append(service)
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

    return (hostgroup, correvent.idcorrevent, event.idevent)

class TestDetailsPlugin(TestController):
    """Teste le dialogue pour l'accès aux historiques."""

    def test_details_plugin_LLS_alert_when_allowed(self):
        """Dialogue des détails avec un LLS et les bons droits."""
        hostgroup, idcorrevent, idcause = insert_deps(True)
        manage = Permission.by_permission_name(u'manage')
        manage.hostgroups.append(hostgroup)
        DBSession.flush()
        transaction.commit()

        response = self.app.post('/get_plugin_value', {
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
            "initial_state": "WARNING"
        })

    def test_details_plugin_host_alert_when_allowed(self):
        """Dialogue des détails avec un hôte et les bons droits."""
        hostgroup, idcorrevent, idcause = insert_deps(False)
        manage = Permission.by_permission_name(u'manage')
        manage.hostgroups.append(hostgroup)
        DBSession.flush()
        transaction.commit()

        response = self.app.post('/get_plugin_value', {
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
            "initial_state": "WARNING"
        })


    def test_details_plugin_LLS_when_forbidden(self):
        """Dialogue des détails avec un LLS et des droits insuffisants."""
        idcorrevent = insert_deps(True)[1]
        DBSession.flush()
        transaction.commit()

        # Le contrôleur renvoie une erreur 404 (HTTPNotFound)
        # lorsque l'utilisateur n'a pas les permissions nécessaires sur
        # les données ou qu'aucun événement correspondant n'est trouvé.
        self.app.post('/get_plugin_value', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, extra_environ={'REMOTE_USER': 'manager'},
            status=404)

    def test_details_plugin_host_when_forbidden(self):
        """Dialogue des détails avec un hôte et des droits insuffisants."""
        idcorrevent = insert_deps(False)[1]
        DBSession.flush()
        transaction.commit()

        # Le contrôleur renvoie une erreur 404 (HTTPNotFound)
        # lorsque l'utilisateur n'a pas les permissions nécessaires sur
        # les données ou qu'aucun événement correspondant n'est trouvé.
        self.app.post('/get_plugin_value', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, extra_environ={'REMOTE_USER': 'manager'},
            status=404)

    def test_details_plugin_LLS_anonymous(self):
        """Dialogue des détails avec un LLS et en anonyme."""
        idcorrevent = insert_deps(True)[1]
        DBSession.flush()
        transaction.commit()

        # Le contrôleur renvoie une erreur 401 (HTTPUnauthorized)
        # lorsque l'utilisateur n'est pas authentifié.
        self.app.post('/get_plugin_value', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, status=401)

    def test_details_plugin_host_anonymous(self):
        """Dialogue des détails avec un hôte et en anonyme."""
        idcorrevent = insert_deps(False)[1]
        DBSession.flush()
        transaction.commit()

        # Le contrôleur renvoie une erreur 401 (HTTPUnauthorized)
        # lorsque l'utilisateur n'est pas authentifié.
        self.app.post('/get_plugin_value', {
                'idcorrevent': idcorrevent,
                'plugin_name': 'details',
            }, status=401)


# -*- coding: utf-8 -*-
"""
Teste le formulaire donnant les liens vers les outils extérieurs
et les données de l'historique.
"""
from nose.tools import assert_true, assert_equal
from datetime import datetime
import transaction

from vigiboard.tests import TestController
from vigiboard.model import DBSession, ServiceGroup, HostGroup, \
                            Host, Permission, StateName, \
                            LowLevelService, Event, CorrEvent

def insert_deps(return_service):
    """Insère les dépendances nécessaires aux tests."""
    timestamp = datetime.now()
    DBSession.add(StateName(statename=u'OK', order=1))
    DBSession.add(StateName(statename=u'UNKNOWN', order=1))
    DBSession.add(StateName(statename=u'WARNING', order=1))
    DBSession.add(StateName(statename=u'CRITICAL', order=1))
    DBSession.flush()

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

    return (hostgroup, correvent.idcorrevent)

class TestHistoryForm(TestController):
    """Teste le dialogue pour l'accès aux historiques."""

    def test_history_form_LLS_alert_when_allowed(self):
        """Teste le formulaire d'historique avec un LLS (alerte visible)."""
        hostgroup, idcorrevent = insert_deps(True)
        manage = Permission.by_permission_name(u'manage')
        manage.hostgroups.append(hostgroup)
        DBSession.flush()
        transaction.commit()

        response = self.app.post('/history_dialog',
            {'idcorrevent': idcorrevent},
            extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # Le contenu de "eventdetails" varie facilement.
        # On le teste séparément.
        json.pop('eventdetails', None)
        assert_true('eventdetails' in response.json)

        assert_equal(json, {
            "idcorrevent": idcorrevent,
            "service": "baz",
            "peak_state": "WARNING",
            "current_state": "WARNING",
            "host": "bar",
            "initial_state": "WARNING"
        })

    def test_history_form_host_alert_when_allowed(self):
        """Teste le formulaire d'historique avec un hôte (alerte visible)."""
        hostgroup, idcorrevent = insert_deps(False)
        manage = Permission.by_permission_name(u'manage')
        manage.hostgroups.append(hostgroup)
        DBSession.flush()
        transaction.commit()

        response = self.app.post('/history_dialog',
            {'idcorrevent': idcorrevent},
            extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # Le contenu de "eventdetails" varie facilement.
        # On le teste séparément.
        json.pop('eventdetails', None)
        assert_true('eventdetails' in response.json)

        assert_equal(json, {
            "idcorrevent": idcorrevent,
            "service": None,
            "peak_state": "WARNING",
            "current_state": "WARNING",
            "host": "bar",
            "initial_state": "WARNING"
        })


    def test_history_form_LLS_when_forbidden(self):
        """Teste le formulaire d'historique avec un LLS (alerte invisible)."""
        idcorrevent = insert_deps(True)[1]
        DBSession.flush()
        transaction.commit()

        response = self.app.post('/history_dialog',
            {'idcorrevent': idcorrevent},
            extra_environ={'REMOTE_USER': 'manager'},
            status=302)

    def test_history_form_host_when_forbidden(self):
        """Teste le formulaire d'historique avec un LLS (alerte invisible)."""
        idcorrevent = insert_deps(False)[1]
        DBSession.flush()
        transaction.commit()

        response = self.app.post('/history_dialog',
            {'idcorrevent': idcorrevent},
            extra_environ={'REMOTE_USER': 'manager'},
            status=302)


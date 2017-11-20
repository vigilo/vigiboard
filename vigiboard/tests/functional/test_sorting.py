# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Test du tri de Vigiboard
"""

from __future__ import absolute_import

from nose.tools import assert_true, assert_equal

import transaction
from vigilo.models.demo import functions
from vigilo.models.session import DBSession
from vigilo.models import tables

from vigiboard.tests import TestController
from tg import config

def populate_DB():
    """ Peuple la base de données en vue des tests. """

    # On crée deux hôtes de test.
    host1 = functions.add_host(u'host1')
    host2 = functions.add_host(u'host2')
    DBSession.flush()

    # On ajoute un service sur chaque hôte.
    service1 = functions.add_lowlevelservice(
                        host2, u'service1')
    service2 = functions.add_lowlevelservice(
                        host1, u'service2')
    DBSession.flush()

    # On ajoute un événement brut sur chaque service.
    event1 = functions.add_event(service1, u'WARNING', u'foo')
    event2 = functions.add_event(service2, u'CRITICAL', u'foo')
    DBSession.flush()

    # On ajoute un événement corrélé pour chaque événement brut.
    functions.add_correvent([event1])
    functions.add_correvent([event2])
    DBSession.flush()
    transaction.commit()

class TestSorting(TestController):
    """
    Test du tri de Vigiboard
    """
    def setUp(self):
        super(TestSorting, self).setUp()
        populate_DB()

    def test_ascending_order(self):
        """ Tri dans l'ordre croissant """

        # On affiche la page principale de VigiBoard
        # triée sur le nom d'hôte par ordre croissant
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get(
            '/?search_form:sort=hostname&search_form:order=asc', extra_environ=environ)

        # Il doit y avoir 2 lignes de résultats :
        # - la 1ère concerne 'service2' sur 'host1' ;
        # - la 2nde concerne 'service1' sur 'host2'.
        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        hostnames = response.lxml.xpath(
            '//table[contains(concat(" ", @class, " "), " vigitable ")]'
            '/tbody/tr/td[@class="plugin_hostname"]/text()')
        assert_equal(hostnames, ['host1', 'host2'])
        servicenames = response.lxml.xpath(
            '//table[contains(concat(" ", @class, " "), " vigitable ")]'
            '/tbody/tr/td[@class="plugin_servicename"]/text()')
        assert_equal(servicenames, ['service2', 'service1'])

    def test_descending_order(self):
        """ Tri dans l'ordre décroissant """

        # On affiche la page principale de VigiBoard
        # triée sur le nom de service par ordre décroissant
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get(
            '/?search_form:sort=servicename&search_form:order=desc', extra_environ=environ)

        # Il doit y avoir 2 lignes de résultats :
        # - la 1ère concerne 'service2' sur 'host1' ;
        # - la 2nde concerne 'service1' sur 'host2'.
        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        hostnames = response.lxml.xpath(
            '//table[contains(concat(" ", @class, " "), " vigitable ")]'
            '/tbody/tr/td[@class="plugin_hostname"]/text()')
        assert_equal(hostnames, ['host1', 'host2'])
        servicenames = response.lxml.xpath(
            '//table[contains(concat(" ", @class, " "), " vigitable ")]'
            '/tbody/tr/td[@class="plugin_servicename"]/text()')
        assert_equal(servicenames, ['service2', 'service1'])

    def test_pagination(self):
        """ Pagination du tri """

        # On crée autant d'événements qu'on peut en afficher par page + 1,
        # afin d'avoir 2 pages dans le bac à événements.
        host3 = functions.add_host(u'host3')
        service3 = functions.add_lowlevelservice(
                            host3, u'service3')
        DBSession.flush()
        items_per_page = int(config['vigiboard_items_per_page'])
        for i in range(items_per_page - 1):
            event = functions.add_event(service3, u'WARNING', u'foo')
            functions.add_correvent([event])
            DBSession.flush()
        transaction.commit()

        # On affiche la seconde page de VigiBoard avec
        # un tri par ordre décroissant sur le nom d'hôte
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get(
            '/?page=2&sort=hostname&order=desc', extra_environ=environ)

        # Il ne doit y avoir qu'une seule ligne de
        # résultats concernant "service2" sur "host1"
        hostnames = response.lxml.xpath(
            '//table[contains(concat(" ", @class, " "), " vigitable ")]'
            '/tbody/tr/td[@class="plugin_hostname"]/text()')
        assert_equal(hostnames, ['host1'])
        servicenames = response.lxml.xpath(
            '//table[contains(concat(" ", @class, " "), " vigitable ")]'
            '/tbody/tr/td[@class="plugin_servicename"]/text()')
        assert_equal(servicenames, ['service2'])



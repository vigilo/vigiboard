# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2012 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Test du tableau d'événements de Vigiboard
"""

from __future__ import absolute_import

from nose.tools import assert_true, assert_equal

from vigiboard.tests import TestController

from .utils import populate_DB


class TestEventTable(TestController):
    """
    Test du tableau d'événements de Vigiboard
    """
    def setUp(self):
        super(TestEventTable, self).setUp()
        populate_DB()

    def test_homepage(self):
        """
        Tableau des événements (page d'accueil).
        """
        # L'utilisateur n'est pas authentifié.
        response = self.app.get('/', status=401)
        response = self.app.get('/index.csv', status=401)

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

        # Mêmes vérifications pour le CSV.
        response = self.app.get('/index.csv', extra_environ=environ)
        # 1 ligne d'en-tête + 2 lignes de données
        lines = response.body.strip().splitlines()
        assert_equal(3, len(lines))
        assert_true(len(lines[0].split(';')) > 1)


        # L'utilisateur est authentifié avec des permissions plus étendues.
        environ = {'REMOTE_USER': 'access'}
        response = self.app.get('/', extra_environ=environ)

        # Il doit y avoir 5 lignes de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 5)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

        # Mêmes vérifications pour le CSV.
        response = self.app.get('/index.csv', extra_environ=environ)
        # 1 ligne d'en-tête + 5 lignes de données
        lines = response.body.strip().splitlines()
        assert_equal(6, len(lines))
        assert_true(len(lines[0].split(';')) > 1)


        # L'utilisateur fait partie du groupe 'managers'
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get('/', extra_environ=environ)

        # Il doit y avoir 5 lignes de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 5)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

        # Mêmes vérifications pour le CSV.
        response = self.app.get('/index.csv', extra_environ=environ)
        # 1 ligne d'en-tête + 5 lignes de données
        lines = response.body.strip().splitlines()
        assert_equal(6, len(lines))
        assert_true(len(lines[0].split(';')) > 1)

    def test_correvents_table_for_LLS(self):
        """
        Tableau des événements corrélés pour un service de bas niveau.
        """
        url = '/item/1/%s/%s' % ('group2_host', 'group2_service')

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

        # L'utilisateur fait partie du groupe 'managers'
        # Il doit avoir accès à l'historique.
        # Ici, il n'y a qu'un seul événement corrélé pour ce service.
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get(url, extra_environ=environ, status=200)

        # Il doit y avoir 1 ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

    def test_correvents_table_for_host(self):
        """
        Tableau des événements corrélés pour un hôte.
        """
        url = '/item/1/%s/' % ('group2_host', )

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

        # L'utilisateur fait partie du groupe 'managers'.
        # Il doit avoir accès à l'historique.
        # Ici, il n'y a qu'un seul événement corrélé pour ce service.
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get(url, extra_environ=environ, status=200)

        # Il doit y avoir 1 ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

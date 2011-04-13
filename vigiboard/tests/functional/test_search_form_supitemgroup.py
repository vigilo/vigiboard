# -*- coding: utf-8 -*-
"""
Teste le formulaire de recherche avec un groupe d'hôtes.
"""
from nose.tools import assert_true, assert_equal
from datetime import datetime
import transaction

from vigiboard.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.tables import SupItemGroup, Host, Permission, StateName, \
                                    Event, CorrEvent, User, UserGroup, \
                                    DataPermission

from utils import populate_DB

class TestSearchFormSupItemGroup(TestController):
    """Teste la récupération d'événements selon le supitemgroup."""
    def setUp(self):
        super(TestSearchFormSupItemGroup, self).setUp()
        populate_DB()

    def test_search_supitemgroup_when_allowed(self):
        """Teste la recherche par supitemgroup avec les bons droits d'accès."""

        # On récupère les 2 groupes de supitems utilisés lors de ces tests.
        maingroup = SupItemGroup.by_group_name('maingroup')
        group1 = SupItemGroup.by_group_name('group1')

        # L'utilisateur est authentifié avec des permissions réduites.
        # Il effectue une recherche sur un groupe de supitems auquel
        # il a accès, on s'attend à ce que la requête retourne 2 résultats.
        environ = {'REMOTE_USER': 'limited_access'}
        response = self.app.get(
            '/?supitemgroup=%d' % group1.idgroup,
            extra_environ=environ
        )

        # Il doit y avoir 2 lignes dans la réponse.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 2)

        # Il doit y avoir plusieurs colonnes dans la réponse.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

        # Le même utilisateur effectue une recherche sur un groupe de supitems
        # auquel il n'a pas accès, mais qui est parent du groupe précédent.
        # On s'attend donc à ce que la requête retourne également 2 résultats.
        environ = {'REMOTE_USER': 'limited_access'}
        response = self.app.get(
            '/?supitemgroup=%d' % maingroup.idgroup,
            extra_environ=environ
        )

        # Il doit y avoir 2 lignes dans la réponse.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 2)

        # Il doit y avoir plusieurs colonnes dans la réponse.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

        # L'utilisateur est authentifié avec des permissions plus étendues.
        # Il effectue une recherche sur un groupe de supitems auquel
        # il a accès, on s'attend à ce que la requête retourne 5 résultats,
        # dont 4 grâce à l'héritage de permissions entre les groupes.
        environ = {'REMOTE_USER': 'access'}
        response = self.app.get(
            '/?supitemgroup=%d' % maingroup.idgroup,
            extra_environ=environ
        )

        # Il doit y avoir 5 lignes dans la réponse.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 5)

        # Il doit y avoir plusieurs colonnes dans la réponse.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

        # L'utilisateur est authentifié et fait partie du groupe
        # 'managers'. Il effectue une recherche sur un groupe de supitems, 
        # et on s'attend à ce que la requête retourne 5 résultats.
        environ = {'REMOTE_USER': 'access'}
        response = self.app.get(
            '/?supitemgroup=%d' % maingroup.idgroup,
            extra_environ=environ
        )

        # Il doit y avoir 5 lignes dans la réponse.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 5)

        # Il doit y avoir plusieurs colonnes dans la réponse.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

    def test_search_inexistent_supitemgroup(self):
        """Teste la recherche par supitemgroup sur un groupe inexistant."""

        # L'utilisateur est authentifié avec des permissions
        # étendues. Il effectue une recherche sur un groupe d'hôtes
        # qui n'existe pas, il ne doit donc obtenir aucun résultat.
        response = self.app.get('/?supitemgroup=%d' % -42,
            extra_environ={'REMOTE_USER': 'access'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

        # Il doit y avoir 1 seule colonne dans la ligne de résultats.
        # (la colonne contient le texte "Il n'y a aucun événément", traduit)
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_equal(len(cols), 1)

        # L'utilisateur est authentifié et fait partie du groupe
        # 'managers'. Il effectue une recherche sur un groupe d'hôtes
        # qui n'existe pas, il ne doit donc obtenir aucun résultat.
        response = self.app.get('/?supitemgroup=%d' % -42,
            extra_environ={'REMOTE_USER': 'manager'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)

        # Il doit y avoir 1 seule colonne dans la ligne de résultats.
        # (la colonne contient le texte "Il n'y a aucun événément", traduit)
        assert_equal(len(rows), 1)
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_equal(len(cols), 1)

    def test_search_supitemgroup_when_disallowed(self):
        """Teste la recherche par supitemgroup SANS les droits d'accès."""

        # On récupère les 2 groupes de supitems utilisés lors de ces tests.
        maingroup = SupItemGroup.by_group_name('maingroup')
        group2 = SupItemGroup.by_group_name('group2')

        # L'utilisateur n'est pas authentifié.
        response = self.app.get('/', status=401)

        # L'utilisateur est authentifié avec des permissions réduites.
        # Il effectue une recherche sur un groupe de supitems auquel
        # il n'a pas accès, mais qui est le parent d'un groupe auquel
        # il a accès. Il ne doit obtenir aucun résultat.
        environ = {'REMOTE_USER': 'limited_access'}
        response = self.app.get(
            '/?supitemgroup=%d' % maingroup.idgroup,
            extra_environ=environ
        )

        # Il doit y avoir 1 seule ligne dans la réponse.
        # (la réponse contient le texte "Il n'y a aucun événément", traduit)
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

        # Il doit y avoir 1 seule colonne dans la réponse.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_equal(len(cols), 1)

        # L'utilisateur est authentifié avec des permissions réduites.
        # Il effectue une recherche sur un groupe de supitems auquel
        # il n'a pas accès, mais qui est le fils du groupe parent d'un
        # groupe auquel il a accès. Il ne doit donc, là non plus, obtenir
        # aucun résultat.
        environ = {'REMOTE_USER': 'limited_access'}
        response = self.app.get(
            '/?supitemgroup=%d' % group2.idgroup,
            extra_environ=environ
        )

        # Il doit y avoir 1 seule ligne dans la réponse.
        # (la réponse contient le texte "Il n'y a aucun événément", traduit)
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

        # Il doit y avoir 1 seule colonne dans la réponse.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_equal(len(cols), 1)


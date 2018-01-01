# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2018 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Test des vues liées aux règles de mise en silence
"""

from __future__ import absolute_import

from nose.tools import assert_true, assert_equal

import urllib
import transaction

from vigilo.models.demo import functions
from vigilo.models.session import DBSession
from vigilo.models.tables import Silence, SupItem

from vigiboard.tests import TestController
from tg import config

import logging
logging.basicConfig()

def populate_DB():
    """ Peuple la base de données en vue des tests. """

    # On crée quatre hôtes de test.
    host1 = functions.add_host(u'host1')
    host2 = functions.add_host(u'host2')
    host3 = functions.add_host(u'host3')
    host4 = functions.add_host(u'host4')
    DBSession.flush()

    # On ajoute un service sur chaque hôte.
    service1 = functions.add_lowlevelservice(
                        host2, u'service1')
    service2 = functions.add_lowlevelservice(
                        host1, u'service2')
    service3 = functions.add_lowlevelservice(
                        host3, u'service3')
    functions.add_lowlevelservice(
                        host4, u'service4')
    DBSession.flush()

    # On crée un groupe de supitems et on y ajoute 'host1' et 'host4' en vue des
    # tests portant sur les permissions
    group1 = functions.add_supitemgroup(u'group1')
    DBSession.add(group1)
    functions.add_host2group(u'host1', u'group1')
    functions.add_host2group(u'host4', u'group1')
    DBSession.flush()

    # On ajoute 2 utilisateurs.
    functions.add_user(u'no_rights', u'no@righ.ts',
                       u'no_rights', u'no_rights',
                       u'no_rights')
    functions.add_user(u'limited_rights', u'limited@righ.ts',
                       u'limited_rights', u'limited_rights',
                       u'limited_rights')
    functions.add_usergroup_permission(u'limited_rights', u'vigiboard-silence')
    functions.add_supitemgrouppermission(u'group1', u'limited_rights')
    DBSession.flush()

    # On ajoute 4 règles de mise en silence.
    functions.add_silence(
        states=[u'UNKNOWN'], host=host1, service=None, user=u'manager',
        comment=u'foo', date=u'2000-01-01 00:00:00')
    functions.add_silence(
        states=[u'DOWN'], host=host1, service=service2,
        user=u'unrestricted', comment=u'bar', date=u'2000-01-02 00:00:00')
    functions.add_silence(
        states=[u'WARNING', 'CRITICAL'], host=host2, service=service1, user=u'unrestricted',
        comment=u'baz', date=u'2000-01-03 00:00:00')
    functions.add_silence(
        states=[u'DOWN'], host=host3, service=None,
        user=u'manager', comment=u'qux', date=u'2000-01-04 00:00:00')
    DBSession.flush()

    transaction.commit()

class TestSilence(TestController):
    """
    Test de l'inhibition des alarmes dans VigiBoard.
    """
    def setUp(self):
        super(TestSilence, self).setUp()
        populate_DB()

    def test_default_order(self):
        """ Tri par défaut des règles de mise en silence """

        # 1. On essaye d'afficher la table des règles de mise en silence pour
        # l'utilisateur 'no_rights' et on s'assure qu'on reçoit bien une erreur
        # 403
        environ = {'REMOTE_USER': 'no_rights'}
        response = self.app.get('/silence', extra_environ=environ, status=403)

        # 2. On affiche la table des règles de mise en silence avec l'utilisateur
        # 'limited_rights'
        environ = {'REMOTE_USER': 'limited_rights'}
        response = self.app.get('/silence', extra_environ=environ)

        # Il doit y avoir 2 lignes de résultats
        # - la 1ère concerne 'service2' sur 'host1' ;
        # - la 2ème concerne 'host1' ;
        hostnames = response.lxml.xpath(
            '//table/tbody/tr/' \
            'td[@class="hostname"]/text()')
        assert_equal(hostnames, ['host1', 'host1'])
        servicenames = response.lxml.xpath(
            '//table/tbody/tr/' \
            'td[@class="servicename"]/text()')
        assert_equal(servicenames, ['service2'])

        # 3. On affiche la table des règles de mise en silence avec l'utilisateur
        # 'manager'
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get('/silence', extra_environ=environ)

        # Il doit y avoir 4 lignes de résultats
        # - la 1ère concerne 'host3'.
        # - la 2ème concerne 'service1' sur 'host2' ;
        # - la 3ème concerne 'service2' sur 'host1' ;
        # - la 4ème concerne 'host1' ;
        hostnames = response.lxml.xpath(
            '//table/tbody/tr/' \
            'td[@class="hostname"]/text()')
        assert_equal(hostnames, ['host3', 'host2', 'host1', 'host1'])
        servicenames = response.lxml.xpath(
            '//table/tbody/tr/' \
            'td[@class="servicename"]/text()')
        assert_equal(servicenames, ['service1', 'service2'])

    def test_ascending_order(self):
        """ Tri des règles de mise en silence dans l'ordre croissant """

        # 1. On essaye d'afficher la table des règles de mise en silence triée sur
        # le nom d'hôte par ordre croissant avec l'utilisateur 'no_rights' et on
        # s'assure qu'on reçoit bien une erreur 403
        environ = {'REMOTE_USER': 'no_rights'}
        response = self.app.get('/silence?sort=hostname&order=asc',
            extra_environ=environ, status=403)

        # 2. On affiche la table des règles de mise en silence triée sur le nom
        # d'hôte par ordre croissant avec l'utilisateur 'limited_rights'
        environ = {'REMOTE_USER': 'limited_rights'}
        response = self.app.get(
            '/silence?sort=hostname&order=asc', extra_environ=environ)

        # Il doit y avoir 2 lignes de résultats
        # - la 1ère concerne 'host1' ;
        # - la 2ème concerne 'service2' sur 'host1'.
        hostnames = response.lxml.xpath(
            '//table/tbody/tr/' \
            'td[@class="hostname"]/text()')
        assert_equal(hostnames, ['host1', 'host1'])
        servicenames = response.lxml.xpath(
            '//table/tbody/tr/' \
            'td[@class="servicename"]/text()')
        assert_equal(servicenames, ['service2'])

        # 3. On affiche la table des règles de mise en silence triée sur le nom
        # d'hôte par ordre croissant avec l'utilisateur 'manager'
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get(
            '/silence?sort=hostname&order=asc', extra_environ=environ)

        # Il doit y avoir 4 lignes de résultats
        # - la 1ère concerne 'host1' ;
        # - la 2ème concerne 'service2' sur 'host1' ;
        # - la 3ème concerne 'service1' sur 'host2' ;
        # - la 4ème concerne 'host3'.
        hostnames = response.lxml.xpath(
            '//table/tbody/tr/' \
            'td[@class="hostname"]/text()')
        assert_equal(hostnames, ['host1', 'host1', 'host2', 'host3'])
        servicenames = response.lxml.xpath(
            '//table/tbody/tr/' \
            'td[@class="servicename"]/text()')
        assert_equal(servicenames, ['service2', 'service1'])

    def test_descending_order(self):
        """ Tri des règles de mise en silence dans l'ordre décroissant """

        # 1. On essaye d'afficher la table des règles de mise en silence triée
        # sur le nom de service par ordre décroissant avec l'utilisateur
        # 'no_rights' et on s'assure qu'on reçoit bien une erreur 403
        environ = {'REMOTE_USER': 'no_rights'}
        response = self.app.get('/silence?sort=hostname&order=asc',
            extra_environ=environ, status=403)

        # 2. On affiche la table des règles de mise en silence triée sur le nom
        # de service par ordre décroissant avec l'utilisateur 'limited_rights'
        environ = {'REMOTE_USER': 'limited_rights'}
        response = self.app.get(
            '/silence?sort=servicename&order=desc', extra_environ=environ)

        # Il doit y avoir 2 lignes de résultats
        # - la 1ère concerne 'service2' sur 'host1' ;
        # - la 2ème concerne 'host1' ;
        hostnames = response.lxml.xpath(
            '//table/tbody/tr/' \
            'td[@class="hostname"]/text()')
        assert_equal(hostnames, ['host1', 'host1'])
        servicenames = response.lxml.xpath(
            '//table/tbody/tr/' \
            'td[@class="servicename"]/text()')
        assert_equal(servicenames, ['service2'])

        # 3. On affiche la table des règles de mise en silence triée sur le nom
        # de service par ordre décroissant avec l'utilisateur 'manager'
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get(
            '/silence?sort=servicename&order=desc', extra_environ=environ)

        # Il doit y avoir 4 lignes de résultats
        # - la 1ère concerne 'service2' sur 'host1' ;
        # - la 2ème concerne 'service1' sur 'host2' ;
        # - la 3ème concerne 'host1' ;
        # - la 4ème concerne 'host3'.
        hostnames = response.lxml.xpath(
            '//table/tbody/tr/' \
            'td[@class="hostname"]/text()')
        assert_equal(hostnames, ['host1', 'host2', 'host1', 'host3'])
        servicenames = response.lxml.xpath(
            '//table/tbody/tr/' \
            'td[@class="servicename"]/text()')
        assert_equal(servicenames, ['service2', 'service1'])

    def test_rule_creation(self):
        """ Ajout d'une règle de mise en silence """

        # 1. On essaye d'ajouter une règle de mise en silence sur 'service3'
        # avec l'utilisateur 'no_rights' et on s'assure qu'on reçoit bien une
        # erreur 403
        environ = {'REMOTE_USER': 'no_rights'}
        url = '/silence/create_or_modify?' + urllib.urlencode({
                'states':  'CRITICAL',
                'host':    'host3',
                'service': 'service3',
                'comment': 'commentaire accentué'
            })
        self.app.get(url, extra_environ=environ, status=403)

        # 2. On essaye d'ajouter une règle de mise en silence sur 'service3'
        # avec l'utilisateur 'limited_rights' et on s'assure qu'on est bien
        # redirigé sur un message d'erreur
        environ = {'REMOTE_USER': 'limited_rights'}
        url = '/silence/create_or_modify?' + urllib.urlencode({
                'states':  'CRITICAL',
                'host':    'host3',
                'service': 'service3',
                'comment': 'commentaire accentué'
            })
        response = self.app.get(url, extra_environ=environ, status=302)
        response = response.follow(status = 200, extra_environ = environ)
        assert_true(len(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]')))

        # 3. On ajoute une règle de mise en silence sur 'service4' avec
        # l'utilisateur 'limited_rights'
        environ = {'REMOTE_USER': 'limited_rights'}
        url = '/silence/create_or_modify?' + urllib.urlencode({
                'states':  'CRITICAL',
                'host':    'host4',
                'service': 'service4',
                'comment': 'commentaire accentué'
            })
        self.app.get(url, extra_environ=environ)

        # On recherche dans la base toutes les règles concernant 'service4'
        supitem_id = SupItem.get_supitem('host4', 'service4')
        silences = DBSession.query(Silence
            ).filter(Silence.idsupitem == supitem_id
            ).all()

        # On s'assure qu'il n'y en a qu'une, et on vérifie ses propriétés
        assert_equal(len(silences), 1)
        assert_equal([s.statename for s in silences[0].states], ['CRITICAL'])
        assert_equal(silences[0].comment, u'commentaire accentué')
        assert_equal(silences[0].author, u'limited_rights')

        # 4. On ajoute une règle de mise en silence sur 'service3' avec
        # l'utilisateur 'manager'
        environ = {'REMOTE_USER': 'manager'}
        url = '/silence/create_or_modify?' + urllib.urlencode({
                'states':  'CRITICAL',
                'host':    'host3',
                'service': 'service3',
                'comment': 'commentaire accentué'
            })
        self.app.get(url, extra_environ=environ)

        # On recherche dans la base toutes les règles concernant 'service3'
        supitem_id = SupItem.get_supitem('host3', 'service3')
        silences = DBSession.query(Silence
            ).filter(Silence.idsupitem == supitem_id
            ).all()

        # On s'assure qu'il n'y en a qu'une, et on vérifie ses propriétés
        assert_equal(len(silences), 1)
        assert_equal([s.statename for s in silences[0].states], ['CRITICAL'])
        assert_equal(silences[0].comment, u'commentaire accentué')
        assert_equal(silences[0].author, u'manager')

    def test_rule_update(self):
        """ Mise à jour d'une règle de mise en silence """

        # On recherche dans la base l'id de la règle concernant 'service1'
        service1_id = SupItem.get_supitem('host2', 'service1')
        service1_silence_id = DBSession.query(Silence
            ).filter(Silence.idsupitem == service1_id
            ).one().idsilence
        # On recherche dans la base l'id de la règle concernant 'service2'
        service2_id = SupItem.get_supitem('host1', 'service2')
        service2_silence_id = DBSession.query(Silence
            ).filter(Silence.idsupitem == service2_id
            ).one().idsilence

        # 1. On essaye de mettre à jour la règle de mise en silence sur
        # 'service1' avec l'utilisateur 'no_rights' et on s'assure qu'on reçoit
        # bien une erreur 403
        environ = {'REMOTE_USER': 'no_rights'}
        url = '/silence/create_or_modify?' + urllib.urlencode({
                'idsilence':  service1_silence_id,
                'states':  'CRITICAL',
                'host':    'host1',
                'service': 'service2',
                'comment': 'commentaire accentué'
            }) + '&' + urllib.urlencode({'states':  'WARNING'})
        self.app.get(url, extra_environ=environ, status=403)

        # 2. On essaye de mettre à jour la règle de mise en silence sur
        # 'service1' avec l'utilisateur 'limited_rights' et on s'assure qu'on
        # est bien redirigé sur un message d'erreur
        environ = {'REMOTE_USER': 'limited_rights'}
        url = '/silence/create_or_modify?' + urllib.urlencode({
                'idsilence':  service1_silence_id,
                'states':  'CRITICAL',
                'host':    'host2',
                'service': 'service1',
                'comment': 'commentaire accentué'
            }) + '&' + urllib.urlencode({'states':  'WARNING'})
        response = self.app.get(url, extra_environ=environ, status=302)
        response = response.follow(status = 200, extra_environ = environ)
        assert_true(len(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]')))

        # 3. On met à jour la règle de mise en silence sur 'service2' avec
        # l'utilisateur 'limited_rights'
        environ = {'REMOTE_USER': 'limited_rights'}
        url = '/silence/create_or_modify?' + urllib.urlencode({
                'idsilence':  service2_silence_id,
                'states':  'CRITICAL',
                'host':    'host1',
                'service': 'service2',
                'comment': 'commentaire accentué'
            }) + '&' + urllib.urlencode({'states':  'WARNING'})
        self.app.get(url, extra_environ=environ)

        # On recherche dans la base toutes les règles concernant 'service2'
        silences = DBSession.query(Silence
            ).filter(Silence.idsupitem == service2_id
            ).all()

        # On s'assure qu'il n'y en a qu'une, et on vérifie ses propriétés
        assert_equal(len(silences), 1)
        assert_equal(silences[0].idsilence, service2_silence_id)
        assert_equal(list(set([s.statename for s in silences[0].states]) -
            set([u'CRITICAL', u'WARNING'])), [])
        assert_equal(silences[0].comment, u'commentaire accentué')
        assert_equal(silences[0].author, u'limited_rights')

        # 4. On met à jour la règle de mise en silence sur 'service1' avec
        # l'utilisateur 'manager'
        environ = {'REMOTE_USER': 'manager'}
        url = '/silence/create_or_modify?' + urllib.urlencode({
                'idsilence':  service1_silence_id,
                'states':  'CRITICAL',
                'host':    'host2',
                'service': 'service1',
                'comment': 'commentaire accentué'
            }) + '&' + urllib.urlencode({'states':  'WARNING'})
        self.app.get(url, extra_environ=environ)

        # On recherche dans la base toutes les règles concernant 'service1'
        silences = DBSession.query(Silence
            ).filter(Silence.idsupitem == service1_id
            ).all()

        # On s'assure qu'il n'y en a qu'une, et on vérifie ses propriétés
        assert_equal(len(silences), 1)
        assert_equal(silences[0].idsilence, service1_silence_id)
        assert_equal(list(set([s.statename for s in silences[0].states]) -
            set([u'CRITICAL', u'WARNING'])), [])
        assert_equal(silences[0].comment, u'commentaire accentué')
        assert_equal(silences[0].author, u'manager')

    def test_rule_deletion(self):
        """ Suppression d'une règle de mise en silence """

        # On recherche dans la base l'id de la règle concernant 'service1'
        service1_id = SupItem.get_supitem('host2', 'service1')
        service1_silence_id = DBSession.query(Silence
            ).filter(Silence.idsupitem == service1_id
            ).one().idsilence
        # On recherche dans la base l'id de la règle concernant 'service2'
        service2_id = SupItem.get_supitem('host1', 'service2')
        service2_silence_id = DBSession.query(Silence
            ).filter(Silence.idsupitem == service2_id
            ).one().idsilence

        # On essaye de supprimer la règle de mise en silence portant sur
        # 'service1' avec l'utilisateur 'no_rights' et on s'assure qu'on reçoit
        # bien une erreur 403
        environ = {'REMOTE_USER': 'no_rights'}
        url = '/silence/delete?id=%s' % service1_silence_id
        response = self.app.get(url, extra_environ=environ, status=403)

        # On essaye de supprimer la règle de mise en silence portant sur
        # 'service1' avec l'utilisateur 'limited_rights' et on s'assure qu'on
        # est bien redirigé sur un message d'erreur
        environ = {'REMOTE_USER': 'limited_rights'}
        url = '/silence/delete?id=%s' % service1_silence_id
        response = self.app.get(url, extra_environ=environ, status=302)
        response = response.follow(status = 200, extra_environ = environ)
        assert_true(len(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]')))

        # On supprime la règle de mise en silence portant sur 'service2' avec
        # l'utilisateur 'limited_rights'
        environ = {'REMOTE_USER': 'limited_rights'}
        url = '/silence/delete?id=%s' % service2_silence_id
        response = self.app.get(url, extra_environ=environ)
        # On s'assure qu'elle n'existe plus en base
        silences = DBSession.query(Silence
            ).filter(Silence.idsupitem == service2_silence_id
        ).all()
        assert_equal(len(silences), 0)

        # On supprime la règle de mise en silence portant sur 'service1' avec
        # l'utilisateur 'manager'
        environ = {'REMOTE_USER': 'manager'}
        url = '/silence/delete?id=%s' % service1_silence_id
        response = self.app.get(url, extra_environ=environ)
        # On s'assure qu'elle n'existe plus en base
        silences = DBSession.query(Silence
            ).filter(Silence.idsupitem == service1_id
        ).all()
        assert_equal(len(silences), 0)

class TestSilencePagination(TestController):
    """
    Test de la pagination de la table des règles d'inhibition dans VigiBoard.
    """
    application_under_test = 'pagination'

    def setUp(self):
        super(TestSilencePagination, self).setUp()
        populate_DB()

    def test_pagination(self):
        """ Pagination des règles de mise en silence """

        # On affiche la seconde page de la table des règles de mise en silence
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get('/silence?page=2', extra_environ=environ)

        # Il ne doit y avoir qu'une seule ligne de
        # résultats concernant "service2" sur "host1"
        hostnames = response.lxml.xpath(
            '//table/tbody/tr/' \
            'td[@class="hostname"]/text()')
        assert_equal(hostnames, ['host2'])
        servicenames = response.lxml.xpath(
            '//table/tbody/tr/' \
            'td[@class="servicename"]/text()')
        assert_equal(servicenames, ['service1'])



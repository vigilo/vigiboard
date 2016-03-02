# -*- coding: utf-8 -*-
# Copyright (C) 2006-2016 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Integration tests for the :mod:`repoze.who`-powered authentication sub-system.

As vigiboard grows and the authentication method changes, only these tests
should be updated.

"""

from vigiboard.tests import TestController


class TestAuthentication(TestController):
    """
    Tests for the default authentication setup.

    By default in TurboGears 2, :mod:`repoze.who` is configured with the same
    plugins specified by repoze.what-quickstart (which are listed in
    http://code.gustavonarea.net/repoze.what-quickstart/#repoze.what.plugins.quickstart.setup_sql_auth).

    As the settings for those plugins change, or the plugins are replaced,
    these tests should be updated.

    """

    application_under_test = 'main'

    def test_voluntary_login(self):
        """Voluntary logins must work correctly"""
        # Going to the login form voluntarily:
        resp = self.app.get('/login', status=200)
        form = resp.form
        # Submitting the login form:
        form['login'] = u'manager'
        form['password'] = u'iddad'
        post_login = form.submit(status=302)
        # Being redirected to the home page:
        assert post_login.location.startswith('/post_login') or \
            post_login.location.startswith('http://localhost/post_login'), \
            "Result: %s" % post_login.location
        home_page = post_login.follow(status=302)
        assert 'authtkt' in home_page.request.cookies, \
               'Session cookie was not defined: %s' % home_page.request.cookies
        assert home_page.location == 'http://localhost/'

    def test_logout(self):
        """Logouts must work correctly"""
        # Logging in voluntarily the quick way:
        resp = self.app.get('/login_handler?login=manager&password=iddad',
                            status=302)
        resp = resp.follow(status=302)
        assert 'authtkt' in resp.request.cookies, \
               'Session cookie was not defined: %s' % resp.request.cookies
        # Logging out:
        resp = self.app.get('/logout_handler', status=302,
                            extra_environ={'REMOTE_ADDR': '127.0.0.1'})
        assert resp.location.startswith('/post_logout') or \
            resp.location.startswith('http://localhost/post_logout'), \
            "Result: %s" % resp.location
        # Finally, redirected to the home page:
        home_page = resp.follow(status=302)
        assert home_page.request.cookies.get('authtkt') == '' \
                or home_page.request.cookies.get('authtkt') == 'INVALID', \
               'Session cookie was not deleted: %s' % home_page.request.cookies
        assert home_page.location == 'http://localhost/', home_page.location

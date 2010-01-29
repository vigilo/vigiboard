# -*- coding: utf-8 -*-
"""
Functional test suite for the root controller.

This is an example of how functional tests can be written for controllers.

As opposed to a unit-test, which test a small unit of functionality,
functional tests exercise the whole application and its WSGI stack.

Please read http://pythonpaste.org/webtest/ for more information.

"""
from nose.tools import assert_true

from vigiboard.tests import TestController


class TestRootController(TestController):
    """ Classe de test du root controller """
    def test_index(self):
        """Test that access to the root webpage is restricted."""

        response = self.app.get('/', status=401)
        msg = 'Unauthorized'
        assert_true(msg in response)


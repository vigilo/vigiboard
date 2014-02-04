# -*- coding: utf-8 -*-
# Copyright (C) 2006-2014 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Unit and functional test suite for vigiboard."""

from os import path, environ
import sys

import unittest
from tg import config
from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from webtest import TestApp

from vigilo.models.session import metadata, DBSession

__all__ = ['setup_db', 'teardown_db', 'TestController']

def setup_db():
    """Method used to build a database"""
    print "Creating model"
    engine = config['pylons.app_globals'].sa_engine
    metadata.create_all(engine)

def teardown_db():
    """Method used to destroy a database"""
    print "Destroying model"
    engine = config['pylons.app_globals'].sa_engine
    metadata.drop_all(engine)

class TestController(unittest.TestCase):
    """
    Base functional test case for the controllers.

    The vigiboard application instance (``self.app``) set up in this test
    case (and descendants) has authentication disabled, so that developers can
    test the protected areas independently of the :mod:`repoze.who` plugins
    used initially. This way, authentication can be tested once and separately.

    Check vigiboard.tests.functional.test_authentication for the repoze.who
    integration tests.

    This is the officially supported way to test protected areas with
    repoze.who-testutil (http://code.gustavonarea.net/repoze.who-testutil/).

    """

    application_under_test = 'main_without_authn'

    def setUp(self):
        """Method called by nose before running each test"""
        # Loading the application:
        conf_dir = config.here
        wsgiapp = loadapp('config:test.ini#%s' %
            self.application_under_test, relative_to=conf_dir)
        self.app = TestApp(wsgiapp)
        # Setting it up:
        test_file = path.join(conf_dir, 'test.ini')
        cmd = SetupCommand('setup-app')
        cmd.run([test_file])

    def tearDown(self):
        """Method called by nose after running each test"""
        # Cleaning up the database:
        teardown_db()
        del self.app

# -*- coding: utf-8 -*-
"""Unit and functional test suite for vigiboard."""

from os import path, environ
import sys

import unittest
from tg import config
from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from routes import url_for
from webtest import TestApp

from vigilo.models.session import metadata, DBSession

__all__ = ['setup_db', 'teardown_db', 'TestController', 'url_for']

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

        # Ajout de l'utilisateur 'editor' et de ses permissions limitées.
        # Utilisé pour vérifier la gestion des permissions.
        from vigilo.models import tables
        editor = tables.User()
        editor.user_name = u'editor'
        editor.email = u'editor@somedomain.com'
        editor.fullname = u'Editor'
        editor.password = u'editpass'
        DBSession.add(editor)
        DBSession.flush()

        group = tables.UserGroup()
        group.group_name = u'editors'
        group.users.append(editor)
        DBSession.add(group)
        DBSession.flush()

        permission = tables.Permission()
        permission.permission_name = u'edit'
        permission.usergroups.append(group)
        DBSession.add(permission)
        DBSession.flush()

        permission = tables.Permission.by_permission_name(u'vigiboard-read')
        permission.usergroups.append(group)
        DBSession.flush()

        permission = tables.Permission.by_permission_name(u'vigiboard-write')
        permission.usergroups.append(group)
        DBSession.flush()

        import transaction
        transaction.commit()


    def tearDown(self):
        """Method called by nose after running each test"""
        # Cleaning up the database:
        teardown_db()
        del self.app


# -*- coding: utf-8 -*-
"""Setup the vigiboard application"""

import logging

import transaction
from tg import config

from vigiboard.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)


def setup_app(command, conf, variables):
    """Place any commands to setup vigiboard here"""
    load_environment(conf.global_conf, conf.local_conf)

    # Load the models
    from vigiboard import model

    # Create tables
    print "Creating tables"
    model.metadata.create_all()

    # Create a test used called "manager".
    manager = model.User()
    manager.user_name = u'manager'
    manager.email = u'manager@somedomain.com'
    model.DBSession.add(manager)

    # Create a test group called "managers"
    # and add "manager" to that group.
    group = model.UserGroup()
    group.group_name = u'managers'
    group.users.append(manager)
    model.DBSession.add(group)

    # Create a test permission called "manage"
    # and give it to the group of "managers".
    permission = model.Permission()
    permission.permission_name = u'manage'
    permission.usergroups.append(group)
    model.DBSession.add(permission)

    # Create a test user called "editor".
    editor = model.User()
    editor.user_name = u'editor'
    editor.email = u'editor@somedomain.com'
    model.DBSession.add(editor)

    # Create a test group called "editors"
    # and add "editor" to that group.
    group = model.UserGroup()
    group.group_name = u'editors'
    group.users.append(editor)
    group.users.append(manager)
    model.DBSession.add(group)

    # Create a test permission called "edit"
    # and give it to the group of "editors".
    permission = model.Permission()
    permission.permission_name = u'edit'
    permission.usergroups.append(group)
    model.DBSession.add(permission)

    version = model.Version()
    version.name = u'vigiboard'
    version.version = config['vigiboard_version']
    model.DBSession.add(version)

    model.DBSession.flush()
    transaction.commit()
    print "Successfully setup"

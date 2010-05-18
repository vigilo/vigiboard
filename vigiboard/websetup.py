# -*- coding: utf-8 -*-
"""Setup the vigiboard application"""

__all__ = ['setup_app', 'populate_db']

def setup_app(command, conf, variables):
    """Place any commands to setup vigiboard here"""
    from vigilo.turbogears import populate_db
    from vigiboard.config.environment import load_environment

    load_environment(conf.global_conf, conf.local_conf)
    populate_db()

def populate_db(bind):
    from vigilo.models.session import DBSession
    from vigilo.models import tables

    print "Testing whether VigiBoard was already installed"
    installed = DBSession.query(
            tables.Permission.permission_name
        ).filter(tables.Permission.permission_name == u'vigiboard-access'
        ).scalar()

    if installed:
        print "VigiGraph has already been installed"
        return

    DBSession.add(tables.Permission(
        permission_name=u'vigiboard-access',
        description=u'Gives access to VigiBoard',
    ))
    DBSession.flush()

    DBSession.add(tables.Permission(
        permission_name=u'vigiboard-update',
        description=u'Allows users to update events',
    ))
    DBSession.flush()

    DBSession.add(tables.Permission(
        permission_name=u'vigiboard-admin',
        description=u'Allows users to forcefully close events',
    ))
    DBSession.flush()


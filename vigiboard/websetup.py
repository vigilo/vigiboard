# -*- coding: utf-8 -*-
"""Setup the vigiboard application"""

import logging

from vigiboard.config.environment import load_environment
from vigilo.turbogears import populate_db

__all__ = ['setup_app']

log = logging.getLogger(__name__)


def setup_app(command, conf, variables):
    """Place any commands to setup vigiboard here"""
    load_environment(conf.global_conf, conf.local_conf)
    populate_db()

def init_db():
    """
    Cette fonction est appelée par le script vigiboard-init-db
    pour initialiser la base de données de VigiBoard.
    """
    from paste.script.appinstall import SetupCommand
    import os.path, os

    ini_file = os.getenv("VIGILO_SETTINGS",
                         "/etc/vigilo/vigiboard/settings.ini")

    cmd = SetupCommand('setup-app')
    cmd.run([ini_file])


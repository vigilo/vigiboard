# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
"""WSGI middleware initialization for the vigiboard application."""

from vigiboard.config.app_cfg import base_config
from vigiboard.config.environment import load_environment

__all__ = ['make_app']

# Use base_config to setup the necessary PasteDeploy application factory. 
# make_base_app will wrap the TG2 app with all the middleware it needs. 
make_base_app = base_config.setup_tg_wsgi_app(load_environment)


def make_app(global_conf, full_stack=True, **app_conf):
    """
    Set vigiboard up with the settings found in the PasteDeploy configuration
    file used.
    
    This is the PasteDeploy factory for the vigiboard application.
    
    C{app_conf} contains all the application-specific settings (those defined
    under ``[app:main]``).
    
    @param global_conf: The global settings for vigiboard (those
        defined under the ``[DEFAULT]`` section).
    @type global_conf: C{dict}
    @param full_stack: Should the whole TG2 stack be set up?
    @type full_stack: C{str} or C{bool}
    @return: The vigiboard application with all the relevant middleware
        loaded.
    """
    app = make_base_app(global_conf, full_stack=True, **app_conf)

    # Wrap your base TurboGears 2 application with custom middleware here

    return app


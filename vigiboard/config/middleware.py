# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:

"""WSGI middleware initialization for the vigiboard application."""

from vigiboard.config.app_cfg import base_config
from vigiboard.config.environment import load_environment
from vigiboard.config.vigilo_conf import vigilo_mods

__all__ = ['make_app']

# Use base_config to setup the necessary PasteDeploy application factory. 
# make_base_app will wrap the TG2 app with all the middleware it needs. 
make_base_app = base_config.setup_tg_wsgi_app(load_environment)


def make_app(global_conf, full_stack=True, **app_conf):
    """
    Set vigiboard up with the settings found in the PasteDeploy configuration
    file used.
    
    :param global_conf: The global settings for vigiboard (those
        defined under the ``[DEFAULT]`` section).
    :type global_conf: dict
    :param full_stack: Should the whole TG2 stack be set up?
    :type full_stack: str or bool
    :return: The vigiboard application with all the relevant middleware
        loaded.
    
    This is the PasteDeploy factory for the vigiboard application.
    
    ``app_conf`` contains all the application-specific settings (those defined
    under ``[app:main]``.
    
   
    """

    # Petit hack permettant d'importer la configuration de vigiboard

    for mod in vigilo_mods :
        myconf = __import__(
            'vigiboard.config.vigilo_conf.' + mod ,globals(), locals(), [mod + '_config'],-1)
        myconf = getattr(myconf,mod + '_config')
        for conf in myconf:
            app_conf[conf] = myconf[conf]

    app_conf['vigilo_mods'] = vigilo_mods

    app = make_base_app(global_conf, full_stack=True, **app_conf)
    
    # Wrap your base TurboGears 2 application with custom middleware here
    
    return app

# vim: set fileencoding=utf-8 sw=4 ts=4 et :
from __future__ import absolute_import

"""WSGI middleware initialization for the vigiboard application."""
from .app_cfg import base_config
from .environment import load_environment
from .vigiboard_conf import vigiboard_config
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser

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

    for i in vigiboard_config:
        app_conf[i] = vigiboard_config[i]

    # on cré l'application de base
    app = make_base_app(global_conf, full_stack=True, **app_conf)
    
    # on rajoute le path public de l'application
    import vigiboard
    app = Cascade([
        StaticURLParser(global_conf['here'] + '/' + app_conf['appname']  + '/public'),
        StaticURLParser(vigiboard.__file__.rsplit('/',1)[0] + '/public'),app]
        )
    
    return app


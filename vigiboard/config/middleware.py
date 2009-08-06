# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:

"""WSGI middleware initialization for the vigiboard application."""
from vigiboard.config.app_cfg import base_config
from vigiboard.config.environment import load_environment
from vigiboard.config.vigiboard_conf import vigiboard_config
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
    # Petit hack permettant d'importer la configuration de vigiboard
    try:
        # chargement de l'application
        
        myapp = __import__(app_conf['appname'] ,globals(), locals(), [],-1)
        base_config.package = myapp

        # chargement de la conf de l'application
        myconf = __import__(
            app_conf['appname'] + '.config.' + app_conf['appname'] ,globals(), locals(), [app_conf['appname'] + '_config'],-1)
        myconf = getattr(myconf,app_conf['appname'] + '_config')
        for conf in myconf:
            app_conf[conf] = myconf[conf]
    except:
        print "vigilo-core runing without application"

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

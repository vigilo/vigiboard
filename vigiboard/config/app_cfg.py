# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
"""
Global configuration file for TG2-specific settings in vigiboard.

This file complements development/deployment.ini.

Please note that **all the argument values are strings**. If you want to
convert them into boolean, for example, you should use the
:func:`paste.deploy.converters.asbool` function, as in::
    
    from paste.deploy.converters import asbool
    setting = asbool(global_conf.get('the_setting'))
 
"""

from vigilo.turbogears import VigiloAppConfig

import vigiboard
from vigiboard import model
from vigiboard.lib import app_globals, helpers

base_config = VigiloAppConfig('vigiboard')
base_config.renderers = []

base_config.package = vigiboard

#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi')
# if you want raw speed and have installed chameleon.genshi
# you should try to use this renderer instead.
# warning: for the moment chameleon does not handle i18n translations
#base_config.renderers.append('chameleon_genshi')

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = model
base_config.DBSession = model.DBSession

# Configure the authentication backend
base_config.auth_backend = 'sqlalchemy'
base_config.sa_auth.dbsession = model.DBSession
# what is the class you want to use to search for users in the database
base_config.sa_auth.user_class = model.User
# what is the class you want to use to search for groups in the database
base_config.sa_auth.group_class = model.UserGroup
# what is the class you want to use to search for permissions in the database
base_config.sa_auth.permission_class = model.Permission
# The name "groups" is already used for groups of hosts.
# We use "usergroups" when referering to users to avoid confusion.
base_config.sa_auth.translations.groups = 'usergroups'

# override this if you would like to provide a different who plugin for
# managing login and logout of your application
base_config.sa_auth.form_plugin = None

# You may optionally define a page where you want users to be redirected to
# on login:
base_config.sa_auth.post_login_url = '/post_login'

# You may optionally define a page where you want users to be redirected to
# on logout:
base_config.sa_auth.post_logout_url = '/post_logout'


##################################
# Settings specific to Vigiboard #
##################################

# Vigiboard version
base_config['vigilo_version'] = u'2.0-pre0.1'

# Links configuration
# XXX Should be part of ini settings.
# Les elements suivants peuvent etre utilises dans la chaine de formatage :
# - idaggregate : identifiant de l'aggregat (alerte correlee)
# - host : le nom de l'hote concerne par l'alerte
# - service : le nom du service concerne par l'alerte
base_config['vigiboard_links.eventdetails'] = {
    'nagios': ['Nagios host details', 'http://example1.com/%(idaggregate)s'],
    'metrology': ['Metrology details', 'http://example2.com/%(idaggregate)s'],
    'security': ['Security details', 'http://example3.com/%(idaggregate)s'],
    'servicetype': ['Service Type', 'http://example4.com/%(idaggregate)s'],
}

# Plugins to use
# XXX Should be part of ini settings.
base_config['vigiboard_plugins'] = [
    ['shn', 'PluginSHN'],
]


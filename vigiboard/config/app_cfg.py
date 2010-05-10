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
from pylons.i18n import lazy_ugettext as l_

import vigiboard
from vigiboard.lib import app_globals, helpers

base_config = VigiloAppConfig('vigiboard')
base_config.package = vigiboard

# Configure the authentication backend
base_config.auth_backend = 'sqlalchemy'

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

# Configuration des liens
# Les elements suivants peuvent etre utilises dans la chaine de formatage :
# - %(idcorrevent)d : identifiant de l'aggregat (alerte correlee)
# - %(host)s : le nom de l'hote concerne par l'alerte
# - %(service)s : le nom du service concerne par l'alerte
# - %(message) : le message transmis par Nagios dans l'alerte
#
# Permet de satisfaire l'exigence VIGILO_EXIG_VIGILO_BAC_0130.
base_config['vigiboard_links.eventdetails'] = {
    'nagios': ['Nagios host details', 'http://example1.com/%(idcorrevent)d'],
    'metrology': ['Metrology details', 'http://example2.com/%(idcorrevent)d'],
    'security': ['Security details', 'http://example3.com/%(idcorrevent)d'],
    'servicetype': ['Service Type', 'http://example4.com/%(idcorrevent)d'],
    'documentation': ['Documentation', 'http://doc.example.com/?q=%(message)s'],
}

# URL des tickets, possibilités:
# - %(idcorrevent)d
# - %(host)s
# - %(service)s
# - %(tt)s
base_config['vigiboard_links.tt'] = 'http://example4.com/%(idcorrevent)d/%(tt)s'

# Plugins to use
base_config['vigiboard_plugins'] = [
    ('details', 'PluginDetails'),
    ('date', 'PluginDate'),
    ('priority', 'PluginPriority'),
    ('occurrences', 'PluginOccurrences'),
    ('hostname', 'PluginHostname'),
    ('servicename', 'PluginServicename'),
    ('output', 'PluginOutput'),
    ('hls', 'PluginHLS'),
    ('status', 'PluginStatus'),
]

base_config['vigiboard_refresh_times'] = (
    (0, l_('Never')),
    (30, l_('30 seconds')),
    (60, l_('1 minute')),
    (300, l_('5 minutes')),
    (600, l_('10 minutes')),
)


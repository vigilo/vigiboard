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
from vigiboard.lib import app_globals, helpers

base_config = VigiloAppConfig('vigiboard')
base_config.package = vigiboard

##################################
# Settings specific to Vigiboard #
##################################

# Configuration des liens
# Les elements suivants peuvent etre utilises dans la chaine de formatage :
# - %(idcorrevent)d : identifiant de l'aggregat (alerte correlee)
# - %(host)s : le nom de l'hote concerne par l'alerte
# - %(service)s : le nom du service concerne par l'alerte
# - %(message) : le message transmis par Nagios dans l'alerte
#
# Permet de satisfaire l'exigence VIGILO_EXIG_VIGILO_BAC_0130.
base_config['vigiboard_links.eventdetails'] = {
    'nagios': [
        u'Détail de l\'hôte dans Nagios',
        '/nagios/%(host)s/cgi-bin/status.cgi?host=%(host)s'
    ],
    'metrology': [
        u'Détail de la métrologie',
        'http://vigilo.example.com/vigigraph/rpc/fullHostPage?host=%(host)s'
    ],
    'security': [
        u'Détail de la sécurité',
        'http://security.example.com/?host=%(host)s'
    ],
    'inventory': [
        'Inventaire',
        'http://cmdb.example.com/?host=%(host)s'
    ],
    'documentation': [
        'Documentation',
        'http://doc.example.com/?q=%(message)s'
    ],
}

# URL des tickets, possibilités:
# - %(idcorrevent)d
# - %(host)s
# - %(service)s
# - %(tt)s
base_config['vigiboard_links.tt'] = 'http://bugs.example.com/?ticket=%(tt)s'

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

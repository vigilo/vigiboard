# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
# Copyright (C) 2007-2020 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

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
from vigiboard.lib import app_globals # pylint: disable-msg=W0611
# W0611: Unused import: imports nécessaires pour le fonctionnement


import logging
LOGGER = logging.getLogger(__name__)

class VigiboardConfig(VigiloAppConfig):
    def setup_sqlalchemy(self):
        super(VigiboardConfig, self).setup_sqlalchemy()

        # On est obligés d'attendre que la base de données
        # soit configurée pour charger les plugins.
        from pkg_resources import working_set
        from vigiboard.controllers.plugins import VigiboardRequestPlugin
        from tg import config

        plugins = []
        for plugin_name in config['vigiboard_plugins']:
            try:
                ep = working_set.iter_entry_points(
                        "vigiboard.columns", plugin_name).next()
            except StopIteration:
                pass

            if ep.name in dict(plugins):
                continue

            try:
                plugin_class = ep.load(require=True)
                if issubclass(plugin_class, VigiboardRequestPlugin):
                    plugins.append((unicode(ep.name), plugin_class()))
            except Exception: # pylint: disable-msg=W0703
                # W0703: Catch "Exception"
                LOGGER.exception(u'Unable to import plugin %s', plugin_name)

        config['columns_plugins'] = plugins

base_config = VigiboardConfig('VigiBoard')
base_config.package = vigiboard
base_config.mimetype_lookup = {
    '.csv': 'text/csv',
}

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
base_config['vigiboard_links.eventdetails'] = (
    {
        'label': u'Détail de l\'hôte dans Nagios',
        'uri': '/nagios/%(host)s/cgi-bin/status.cgi?host=%(host)s',
    },
    {
        'label': u'Détail de la métrologie',
        'uri': 'http://vigilo.example.com/vigilo/vigigraph/rpc/fullHostPage?host=%(host)s',
    },
    {
        'label': u'Détail de la sécurité',
        'uri': 'http://security.example.com/?host=%(host)s',
    },
    {
        'label': 'Inventaire',
        'uri': 'http://cmdb.example.com/?host=%(host)s',
    },
    {
        'label': 'Documentation',
        'uri': 'http://doc.example.com/?q=%(message)s',
    },
)

# URL des tickets, possibilités:
# - %(idcorrevent)d
# - %(host)s
# - %(service)s
# - %(tt)s
base_config['vigiboard_links.tt'] = 'http://bugs.example.com/?ticket=%(tt)s'

# Plugins to use
base_config['vigiboard_plugins'] = (
#    'id',
    'details',
#    'state',
    'groups',
    'date',
    'priority',
    'occurrences',
#    'address',
    'hostname',
    'servicename',
    'output',
#    'masked_events',
    'hls',
    'status',
#    'test',
    'map',
)

base_config['csv_columns'] = (
    'id',
    'state',
    'initial_state',
    'peak_state',
    'date',
    'duration',
    'priority',
    'occurrences',
    'hostname',
    'servicename',
    'output',
    'ack',
    'trouble_ticket_id',
    'trouble_ticket_link',
)

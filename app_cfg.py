# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
# Copyright (C) 2007-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Additional settings for VigiBoard that can only be represented
using the Python programming language.
"""

import vigiboard
from vigiboard.config.configurator import VigiboardConfigurator

options = {
    # Configuration des liens
    # Les elements suivants peuvent etre utilises dans la chaine de formatage :
    # - %(idcorrevent)d : identifiant de l'aggregat (alerte correlee)
    # - %(host)s : le nom de l'hote concerne par l'alerte
    # - %(service)s : le nom du service concerne par l'alerte
    # - %(message) : le message transmis par Nagios dans l'alerte
    #
    # Permet de satisfaire l'exigence VIGILO_EXIG_VIGILO_BAC_0130.
    'vigiboard_links.eventdetails': (
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
    ),

    # URL des tickets, possibilités:
    # - %(idcorrevent)d
    # - %(host)s
    # - %(service)s
    # - %(tt)s
    'vigiboard_links.tt': 'http://bugs.example.com/?ticket=%(tt)s',

    # Use the following plugins to display various pieces of information
    # on VigiBoard's main page.
    #
    # Each plugin may add zero or more columns to VigiBoard's main page,
    # or it may add fields to VigiBoard's search form.
    #
    # The order is significant (and affects columns / search fields order).
    'vigiboard_plugins': (
        # The 'id' plugin is disabled by default because it serves more as
        # an example and does not add any operationnal value.
        #'id',

        # The 'defaits' plugin adds a link to a menu where additional
        # information about an alarm can be retrieved.
        'details',

        # The 'state' plugin adds a column with the event's current state.
        # The plugin is disabled by default because this information is already
        # visible in other plugins as a color code.
        #'state',

        # This plugin does not add any column to the display,
        # but makes it possible to filter alarms based on the groups
        # the affected host belongs to.
        'groups',

        # This plugin shows the date of the alarm's last occurrence,
        # and the duration since the first occurrence.
        'date',

        # This plugin displays the alarm's priority.
        'priority',

        # This plugin displays the number of occurrences.
        'occurrences',

        # This plugin displays the affected host's address.
        # It is disabled by default because the hostname plugin is preferred.
        #'address',

        # This plugin displays the affected host's name.
        'hostname',

        # This plugin displays the affected service's name, if any.
        'servicename',

        # This plugin displays the alarm's output message.
        'output',

        # This plugin displays the number of events masked by the alarm.
        # It is disabled by default because it is rarely used.
        #'masked_events',

        # This plugin displays the high-level services impacted by the alarm.
        'hls',

        # This plugin displays the acknowledgment status for the alarm.
        # It can also be used to change the acknowledgment status
        # and to assign a ticket to the alarm.
        'status',

        # This plugin displays a static message and serves as an exemple.
        #'test',

        # This plugin provides a way to filter alarms based on maps.
        'map',
    ),

    'csv_columns': (
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
    ),
}

# Create the final configuration for the application
base_config = VigiboardConfigurator('VigiBoard', vigiboard)
base_config.update_blueprint(options)

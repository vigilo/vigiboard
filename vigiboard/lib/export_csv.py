# vim: set fileencoding=utf-8 sw=4 ts=4 et :
################################################################################
#
# Copyright (C) 2007-2014 CS-SI
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
################################################################################

"""Fonction d'export des alertes au format CSV."""

import csv
from cStringIO import StringIO

from tg import config

def export(page, plugins_data):
    buf = StringIO()
    quoting = config.get('csv_quoting', 'ALL').upper()
    if quoting not in ('ALL', 'MINIMAL', 'NONNUMERIC', 'NONE'):
        quoting = 'ALL'
    csv_writer = csv.DictWriter(buf,
        config['csv_columns'],
        extrasaction='ignore',
        delimiter=config.get("csv_delimiter_char", ';'),
        escapechar=config.get("csv_escape_char", '\\'),
        quotechar=config.get("csv_quote_char", '"'),
        quoting=getattr(csv, 'QUOTE_%s' % quoting))
    csv_writer.writerow(dict(zip(config['csv_columns'], config['csv_columns'])))

    for item in page.items:
        values = {}
        for plugin_name, plugin_instance in config['columns_plugins']:
            if plugins_data[plugin_name]:
                values[plugin_name] = repr(plugins_data[plugin_name])
            else:
                for data_key, data_value in \
                    plugin_instance.get_data(item).iteritems():
                    # Pour les valeurs en unicode, on convertit en UTF-8.
                    if isinstance(data_value, unicode):
                        values[data_key] = data_value.encode('utf-8')
                    # Pour le reste, on suppose qu'on peut en obtenir une
                    # représentation adéquate dont l'encodage ne posera pas
                    # de problème.
                    else:
                        values[data_key] = data_value
        csv_writer.writerow(values)
    return buf.getvalue()

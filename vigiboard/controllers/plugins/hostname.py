# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2020 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Un plugin pour VigiBoard qui ajoute une colonne avec le nom de l'hôte
sur lequel porte l'événement corrélé.
"""
import tw.forms as twf
from tg.i18n import lazy_ugettext as l_

from vigilo.models.functions import sql_escape_like
from vigiboard.controllers.plugins import VigiboardRequestPlugin, ITEMS

class PluginHostname(VigiboardRequestPlugin):
    """
    Ajoute une colonne avec le nom de l'hôte impacté par un événement corrélé.
    """
    def get_search_fields(self):
        return [
            twf.TextField(
                'host',
                label_text=l_('Host'),
                validator=twf.validators.String(if_missing=None),
            )
        ]

    def handle_search_fields(self, query, search, state, subqueries):
        if state != ITEMS:
            return

        if search.get('host'):
            host = sql_escape_like(search['host'])
            query.add_filter(query.items.c.hostname.ilike(host))

    def get_data(self, event):
        return {
            'hostname': event.hostname,
        }

    def get_sort_criterion(self, query, column):
        if column == 'hostname':
            return query.items.c.hostname
        return None


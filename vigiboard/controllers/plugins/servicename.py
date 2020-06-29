# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2020 CS GROUP – France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Un plugin pour VigiBoard qui ajoute une colonne avec le nom du service
à l'origine de l'événement corrélé.
"""
import tw.forms as twf
from tg.i18n import lazy_ugettext as l_

from vigilo.models.functions import sql_escape_like
from vigiboard.controllers.plugins import VigiboardRequestPlugin, ITEMS

class PluginServicename(VigiboardRequestPlugin):
    """
    Affiche le nom du service à l'origine de l'événement corrélé.
    Si l'événement corrélé porte directement sur un hôte,
    alors le nom de service vaut None.
    """
    def get_search_fields(self):
        return [
            twf.TextField(
                'service',
                label_text=l_('Service'),
                validator=twf.validators.UnicodeString(if_missing=None),
            )
        ]

    def handle_search_fields(self, query, search, state, subqueries):
        if state != ITEMS:
            return

        if search.get('service'):
            service = sql_escape_like(search['service'])
            query.add_filter(query.items.c.servicename.ilike(service))

    def get_data(self, event):
        return {
            'servicename': event.servicename,
        }

    def get_sort_criterion(self, query, column):
        if column == 'servicename':
            return query.items.c.servicename
        return None


# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2016 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Un plugin pour VigiBoard qui ajoute une colonne avec la sortie
de la commande de test exécutée par Nagios sur cet hôte/service.
"""
import tw.forms as twf
from tg.i18n import lazy_ugettext as l_

from vigilo.models.tables import Event
from vigilo.models.functions import sql_escape_like
from vigiboard.controllers.plugins import VigiboardRequestPlugin, ITEMS

class PluginOutput(VigiboardRequestPlugin):
    """Ajoute une colonne avec le message de Nagios."""
    def get_search_fields(self):
        return [
            twf.TextField(
                'output',
                label_text=l_('Output'),
                validator=twf.validators.UnicodeString(if_missing=None),
            )
        ]

    def handle_search_fields(self, query, search, state, subqueries):
        if state != ITEMS:
            return

        if search.get('output'):
            output = sql_escape_like(search['output'])
            query.add_filter(Event.message.ilike(output))

    def get_data(self, event):
        return {
            'output': event[0].cause.message,
        }

    def get_sort_criterion(self, query, column):
        if column == 'output':
            return Event.message
        return None


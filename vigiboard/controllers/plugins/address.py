# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2018 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Un plugin pour VigiBoard qui ajoute une colonne avec l'adresse (ex: IP)
de l'hôte sur lequel porte l'événement corrélé.
"""
import tw.forms as twf
from tg.i18n import lazy_ugettext as l_

from vigilo.models.functions import sql_escape_like
from vigiboard.controllers.plugins import VigiboardRequestPlugin, ITEMS

class PluginAddress(VigiboardRequestPlugin):
    """
    Ajoute une colonne avec l'adresse de l'hôte impacté.
    """
    def get_search_fields(self):
        return [
            twf.TextField(
                'address',
                label_text=l_('Address'),
                validator=twf.validators.String(if_missing=None),
            )
        ]

    def handle_search_fields(self, query, search, state, subqueries):
        if state != ITEMS:
            return

        if search.get('address'):
            address = sql_escape_like(search['address'])
            query.add_filter(query.items.c.address.ilike(address))

    def get_data(self, event):
        return {
            'address': event.address,
        }

    def get_sort_criterion(self, query, column):
        if column == 'address':
            return query.items.c.address
        return None


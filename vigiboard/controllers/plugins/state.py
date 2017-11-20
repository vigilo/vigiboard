# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Un plugin pour VigiBoard qui ajoute une colonne avec l'état de l'alerte.
"""
import urllib
import tg
import tw2.forms as twf
from formencode import validators
from tg.i18n import lazy_ugettext as l_

from vigilo.models.tables import CorrEvent, Event, StateName
from vigilo.models.session import DBSession
from vigiboard.controllers.plugins import VigiboardRequestPlugin, ITEMS

class PluginState(VigiboardRequestPlugin):
    """
    Ajoute des colonnes permettant de voir le statut d'acquittement
    d'un événement corrélé et de modifier certaines de ses propriétés.
    """

    def get_search_fields(self):
        states = DBSession.query(StateName.idstatename, StateName.statename
            ).order_by(StateName.order.asc()).all()
        options = [(str(s.idstatename), s.statename, {'title': l_(s.statename)})
                   for s in states]
        return [
            twf.MultipleSelectField(
                'state',
                label=l_('Current state'),
                prompt_text=None,
                options=options,
                item_validator=validators.OneOf(
                    [opt[0] for opt in options],
                    if_invalid=None,
                    if_missing=None,
                ),
            ),
        ]

    def handle_search_fields(self, query, search, state, subqueries):
        if state != ITEMS:
            return

        if search.get('state'):
            try:
                query.add_filter(Event.current_state == int(search['state']))
            except (ValueError, TypeError):
                # On ignore silencieusement le critère de recherche erroné.
                pass

    def get_data(self, event):
        cause = event[0].cause
        state = StateName.value_to_statename(cause.current_state)
        return {'state': state}

    def get_sort_criterion(self, query, column):
        if column == 'state':
            return Event.current_state
        return None


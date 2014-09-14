# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
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

"""
Un plugin pour VigiBoard qui ajoute une colonne avec l'état de l'alerte.
"""
import urllib
import tg
import tw.forms as twf
from pylons.i18n import lazy_ugettext as l_

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
        options = [('', u'')] + \
                    [( str(s.idstatename), s.statename ) for s in states]
        return [
            twf.SingleSelectField(
                'state',
                label_text=l_('Current state'),
                options=options,
                validator=twf.validators.OneOf(
                    dict(options).keys(),
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


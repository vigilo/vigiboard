# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Un plugin pour VigiBoard qui ajoute une colonne avec la date à laquelle
est survenu un événement et la durée depuis laquelle l'événement est actif.
"""
import tw2.forms as twf
from datetime import datetime, timedelta
from tg.i18n import ugettext as _, lazy_ugettext as l_

from vigilo.models import tables
from vigilo.turbogears import widgets

from vigiboard.controllers.plugins import VigiboardRequestPlugin, ITEMS
from vigiboard.lib import error_handler


class PluginDate(VigiboardRequestPlugin):
    """Plugin pour l'ajout d'une colonne Date."""
    def get_search_fields(self):
        return [
            twf.Label('date', text=l_('Last occurrence')),
            widgets.CalendarDateTimePicker(
                'from_date',
                label=l_('Between'),
                button_text=l_("Choose"),
                not_empty=False,
            ),
            widgets.CalendarDateTimePicker(
                'to_date',
                label=l_('And'),
                button_text=l_("Choose"),
                not_empty=False,
            ),
        ]

    def handle_search_fields(self, query, search, state, subqueries):
        if state != ITEMS:
            return

        if search.get('from_date'):
            query.add_filter(tables.CorrEvent.timestamp_active >=
                search['from_date'])

            # Ajout de contrôles sur la date de début
            if search['from_date'] >= datetime.utcnow():
                error_handler.handle_error_message(
                    _('Start date cannot be greater than current date'))

            if search.get('to_date') and \
               search['from_date'] > search['to_date']:
                error_handler.handle_error_message(
                    _('Start date cannot be greater than end date'))

        if search.get('to_date'):
            query.add_filter(tables.CorrEvent.timestamp_active <=
                search['to_date'])

            # Ajout de contrôles sur la date de fin
            if search['to_date'] >= datetime.utcnow():
                error_handler.handle_error_message(
                    _('End date cannot be greater than current date'))

    def get_data(self, event):
        state = tables.StateName.value_to_statename(
                    event[0].cause.current_state)
        # La résolution maximale de Nagios est la seconde.
        # On supprime les microsecondes qui ne nous apportent
        # aucune information et fausse l'affichage dans l'export CSV
        # en créant un nouvel objet timedelta dérivé du premier.
        duration = datetime.utcnow() - event[0].timestamp_active
        duration = timedelta(days=duration.days, seconds=duration.seconds)
        return {
            'state': state,
            'date': event[0].cause.timestamp,
            'duration': duration,
        }

    def get_sort_criterion(self, query, column):
        if column == 'date':
            return tables.Event.timestamp
        return None


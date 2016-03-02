# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
################################################################################
#
# Copyright (C) 2007-2016 CS-SI
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
Un plugin pour VigiBoard qui ajoute une colonne avec la date à laquelle
est survenu un événement et la durée depuis laquelle l'événement est actif.
"""
from datetime import datetime, timedelta
import tw.forms as twf
from pylons.i18n import ugettext as _, lazy_ugettext as l_

from vigilo.models import tables

from vigiboard.controllers.plugins import VigiboardRequestPlugin, ITEMS
from vigiboard.lib import dateformat, error_handler


class ExampleDateFormat(object):
    """
    Une classe permettant d'obtenir un exemple de date
    correspondant au format de la locale de l'utilisateur.
    """
    def __str__(self):
        """
        Retourne l'heure courante au format attendu,
        encodée en UTF-8.

        @return: Heure courante au format attendu (en UTF-8).
        @rtype: C{str}
        """
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        """
        Retourne l'heure courante au format attendu.

        @return: Heure courante au format attendu.
        @rtype: C{unicode}
        """
        format = dateformat.get_date_format()
        date = datetime.strftime(datetime.now(), format).decode('utf-8')
        return _('Eg. %(date)s') % {'date': date}


class PluginDate(VigiboardRequestPlugin):
    """Plugin pour l'ajout d'une colonne Date."""
    def get_search_fields(self):
        return [
            twf.Label('date', text=l_('Last occurrence')),
            twf.CalendarDateTimePicker(
                'from_date',
                label_text=l_('Between'),
                button_text=l_("Choose"),
                not_empty=False,
                validator=dateformat.DateFormatConverter(if_missing=None),
                date_format=dateformat.get_date_format,
                calendar_lang=dateformat.get_calendar_lang,
                attrs={
                    # Affiche un exemple de date au survol
                    # et en tant qu'indication (placeholder).
                    'title': ExampleDateFormat(),
                    'placeholder': ExampleDateFormat()
                },
            ),
            twf.CalendarDateTimePicker(
                'to_date',
                label_text=l_('And'),
                button_text=l_("Choose"),
                not_empty=False,
                validator=dateformat.DateFormatConverter(if_missing=None),
                date_format=dateformat.get_date_format,
                calendar_lang=dateformat.get_calendar_lang,
                attrs={
                    # Affiche un exemple de date au survol
                    # et en tant qu'indication (placeholder).
                    'title': ExampleDateFormat(),
                    'placeholder': ExampleDateFormat()
                },
            ),
        ]

    def handle_search_fields(self, query, search, state, subqueries):
        if state != ITEMS:
            return

        if search.get('from_date'):
            query.add_filter(tables.CorrEvent.timestamp_active >=
                search['from_date'])

            # Ajout de contrôles sur la date de début
            if search['from_date'] >= datetime.now():
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
            if search['to_date'] >= datetime.now():
                error_handler.handle_error_message(
                    _('End date cannot be greater than current date'))

    def get_data(self, event):
        state = tables.StateName.value_to_statename(
                    event[0].cause.current_state)
        # La résolution maximale de Nagios est la seconde.
        # On supprime les microsecondes qui ne nous apportent
        # aucune information et fausse l'affichage dans l'export CSV
        # en créant un nouvel objet timedelta dérivé du premier.
        duration = datetime.now() - event[0].timestamp_active
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


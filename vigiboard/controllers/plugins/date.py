# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
################################################################################
#
# Copyright (C) 2007-2011 CS-SI
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
import tw.forms as twf
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tg.i18n import get_lang
import tg

from vigilo.models import tables

from vigiboard.controllers.plugins import VigiboardRequestPlugin
from vigiboard.lib.dateformat import DateFormatConverter

def get_calendar_lang():
    # TODO: Utiliser le champ "language" du modèle pour cet utilisateur ?
    # On récupère la langue du navigateur de l'utilisateur
    lang = get_lang()
    if not lang:
        lang = tg.config['lang']
    else:
        lang = lang[0]

    # TODO: Il faudrait gérer les cas où tout nous intéresse dans "lang".
    # Si l'identifiant de langage est composé (ex: "fr_FR"),
    # on ne récupère que la 1ère partie.
    lang = lang.replace('_', '-')
    lang = lang.split('-')[0]
    return lang

def get_date_format():
    # @HACK: nécessaire car l_() retourne un object LazyString
    # qui n'est pas sérialisable en JSON.
    return _('%Y-%m-%d %I:%M:%S %p').encode('utf-8')

class PluginDate(VigiboardRequestPlugin):
    """Plugin pour l'ajout d'une colonne Date."""
    def get_search_fields(self):
        return [
            twf.CalendarDateTimePicker(
                'from_date',
                label_text=l_('From'),
                button_text=l_("Choose"),
                not_empty=False,
                validator=DateFormatConverter(if_missing=None),
                date_format=get_date_format,
                calendar_lang=get_calendar_lang,
            ),
            twf.CalendarDateTimePicker(
                'to_date',
                label_text=l_('To'),
                button_text=l_("Choose"),
                not_empty=False,
                validator=DateFormatConverter(if_missing=None),
                date_format=get_date_format,
                calendar_lang=get_calendar_lang,
            ),
        ]

    def handle_search_fields(self, query, search):
        if search.get('from_date'):
            query.add_filter(tables.CorrEvent.timestamp_active >=
                search['from_date'])
        if search.get('to_date'):
            query.add_filter(tables.CorrEvent.timestamp_active <=
                search['to_date'])

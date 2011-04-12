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
Un plugin pour VigiBoard qui ajoute une colonne avec le nom de l'hôte
sur lequel porte l'événement corrélé.
"""
import tw.forms as twf
from pylons.i18n import lazy_ugettext as l_

from vigilo.models.functions import sql_escape_like
from vigiboard.controllers.plugins import VigiboardRequestPlugin

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

    def handle_search_fields(self, query, search, subqueries):
        if search.get('host'):
            host = sql_escape_like(search['host'])
            query.add_filter(query.items.c.hostname.ilike(host))

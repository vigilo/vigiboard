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
Un plugin pour VigiBoard qui ajoute une colonne avec le nom du service
à l'origine de l'événement corrélé.
"""
import tw.forms as twf
from pylons.i18n import lazy_ugettext as l_

from vigilo.models.functions import sql_escape_like
from vigiboard.controllers.plugins import VigiboardRequestPlugin

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
                validator=twf.validators.String(if_missing=None),
            )
        ]

    def handle_search_fields(self, query, search, subqueries):
        if search.get('service'):
            service = sql_escape_like(search['service'])
            query.add_filter(query.items.c.servicename.ilike(service))

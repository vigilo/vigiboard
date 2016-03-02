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

"""Le formulaire de recherche/filtrage."""

from pylons.i18n import lazy_ugettext as l_
import tw.forms as twf
import tg

__all__ = (
    'SearchForm',
    'create_search_form',
)

class SearchForm(twf.TableForm):
    """
    Formulaire de recherche dans les événements

    Affiche un champ texte pour l'hôte, le service, la sortie,
    le ticket d'incidence, et la date.

    Ce widget permet de répondre aux exigences suivantes :
        - VIGILO_EXIG_VIGILO_BAC_0070
        - VIGILO_EXIG_VIGILO_BAC_0100
    """

    method = 'GET'
    style = 'display: none'

    # Paramètres liés à la pagination et au tri.
    fields = [
        twf.HiddenField('page'),
        twf.HiddenField('sort'),
        twf.HiddenField('order')
    ]
    for plugin, instance in tg.config.get('columns_plugins', []):
        fields.extend(instance.get_search_fields())

create_search_form = SearchForm("search_form",
    submit_text=l_('Search'), action=tg.url('/'),
)

# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Le formulaire de recherche/filtrage."""

import itertools
from tg.i18n import lazy_ugettext as l_
from formencode import validators
import tw2.core as twc
import tw2.forms as twf
import tg

__all__ = (
    'SearchForm',
    'SearchFormWithSorting',
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
    action = tg.lurl('/')
    submit = twf.SubmitButton(value=l_('Search'))
    id = 'search_form'

    children = [
        field(field.id) for field in
        itertools.chain(*list(
            plugin[1].get_search_fields()
            for plugin in tg.config.get('columns_plugins', [])
        ))
    ]

class SearchFormWithSorting(twc.CompoundWidget):
    id = None

    # Paramètres liés à la pagination et au tri.
    page = twf.HiddenField(validator=validators.Int(
            min=1,
            if_missing=1,
            if_invalid=1,
            not_empty=True
        ))
    sort = twf.HiddenField(validator=validators.UnicodeString(if_missing=''))
    order = twf.HiddenField(validator=validators.OneOf(['asc', 'desc'],
                            if_missing='asc'))

    # Paramètres liés au formulaire de recherche.
    search_form = SearchForm()

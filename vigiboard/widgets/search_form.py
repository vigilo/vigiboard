# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2019 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Le formulaire de recherche/filtrage."""

from tg.i18n import lazy_ugettext as l_
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

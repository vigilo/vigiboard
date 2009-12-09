# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Le formulaire de recherche/filtrage."""

from pylons.i18n import lazy_ugettext as l_
from tw.forms import TableForm, TextField
from tw.api import WidgetsList

__all__ = ('SearchForm', )

class SearchForm(TableForm):
    """
    Formulaire de recherche dans les événements

    Affiche un champ texte pour l'hôte, le service, la sortie
    et le ticket d'incidence.
    """
    class fields(WidgetsList):
        host = TextField(label_text=l_('Host'))
        service = TextField(label_text=l_('Service'))
        output = TextField(label_text=l_('Output'))
        trouble_ticket = TextField(label_text=l_('Trouble Ticket'))

    method = 'GET'
    submit_text = l_('Search')
    style = 'display: none'


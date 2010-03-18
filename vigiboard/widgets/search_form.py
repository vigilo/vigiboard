# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Le formulaire de recherche/filtrage."""

import tg
from pylons.i18n import lazy_ugettext as l_
from tw.api import WidgetsList
from tw.forms import TableForm, TextField, CalendarDateTimePicker, SubmitButton

__all__ = ('SearchForm', 'create_search_form')

class SearchForm(TableForm):
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

    class fields(WidgetsList):
        hostgroup = TextField(label_text=l_('Host group'))
        servicegroup = TextField(label_text=l_('Service group'))
        host = TextField(label_text=l_('Host'))
        service = TextField(label_text=l_('Service'))
        output = TextField(label_text=l_('Output'))
        trouble_ticket = TextField(label_text=l_('Trouble Ticket'))
        from_date = CalendarDateTimePicker(
            label_text = l_('From'),
            button_text = l_("Choose"),
            not_empty = False)
        to_date = CalendarDateTimePicker(
            label_text = l_('To'),
            button_text = l_("Choose"),
            not_empty = False)
    
create_search_form = SearchForm("search_form",
    submit_text=l_('Search'), action=tg.url('/'))


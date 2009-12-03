# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Les différents formulaires de Vigiboard"""

from pylons.i18n import lazy_ugettext as l_
from tw.forms import TableForm, SingleSelectField, TextField, HiddenField

__all__ = ('EditEventForm', 'SearchForm', )

edit_event_status_options = [
    ['NoChange', l_('No change')],
    ['None', l_('Change to None')],
    ['Acknowledged', l_('Change to Acknowledged')],
    ['AAClosed', l_('Change to Closed')],
]

class EditEventForm(TableForm):
    
    """
    Formulaire d'édition d'événement

    Affiche une zone de texte pour le Trouble Ticket et une
    liste déroulante pour le nouveau status
    """

    fields = [
        HiddenField('id'),
        TextField('trouble_ticket', label_text=l_('Trouble Ticket')),
        SingleSelectField('status', label_text=l_('Status'),
            options=edit_event_status_options),
    ]
    submit_text = l_('Apply')

class SearchForm(TableForm):
    
    """
    Formulaire de recherche dans les événements

    Affiche un champ texte pour l'hôte, le service, la sortie
    et le ticket d'incidence.
    """

    fields = [
        TextField('host', label_text=l_('Host')),
        TextField('service', label_text=l_('Service')),
        TextField('output', label_text=l_('Output')),
        TextField('trouble_ticket', label_text=l_('Trouble Ticket')),
    ]

    method = 'GET'
    submit_text = l_('Search')


# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Les différents formulaires de Vigiboard"""

from pylons.i18n import ugettext as _
from tw.forms import TableForm, SingleSelectField, TextField, HiddenField

edit_event_status_options = [
            ['NoChange',_('No change')],
            ['None',_('Change to None')],
            ['Acknowledged',_('Change to Acknowledged')],
            ['AAClosed',_('Change to Closed')]
            ]

class EditEventForm(TableForm):
    
    """
    Formulaire d'édition d'évènement

    Affiche une zone de texte pour le Trouble Ticket et une
    liste déroulante pour le nouveau status
    """

    fields = [
	    HiddenField('id'),
		TextField('trouble_ticket',label_text=_('Touble Ticket')),
		SingleSelectField('status',options=edit_event_status_options)
		]

    submit_text = _('Apply')

class SearchForm(TableForm):
    
    """
    Formulaire de recherche dans les évènements

    Affiche un champ texte pour l'hôte, le service, la sortie et le trouble ticket
    """

    fields = [
		TextField('host',label_text=_('Host')),
		TextField('service',label_text=_('Service')),
		TextField('output',label_text=_('Output')),
		TextField('trouble_ticket',label_text=_('Trouble Ticket')),
		]

    submit_text = _('Search')

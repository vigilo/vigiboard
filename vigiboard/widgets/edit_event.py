# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Le formulaire d'édition d'un événement."""

from pylons.i18n import lazy_ugettext as l_
from tw.forms import TableForm, SingleSelectField, TextField, \
                        HiddenField, SubmitButton
from tw.api import WidgetsList

__all__ = ('EditEventForm', 'edit_event_status_options')

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

    submit_text = None
    fields = [
        HiddenField('id'),
        TextField('trouble_ticket', label_text=l_('Trouble Ticket')),
        SingleSelectField('ack', label_text=l_('Status'), 
                                            options=edit_event_status_options)
    ]
    
    def __init__(self, id, last_modification, *args, **kwargs):
        super(TableForm, self).__init__(id, *args, **kwargs)

        self.children.append(HiddenField('last_modification',
                                         attrs={'value': last_modification}))
        self.children.append(SubmitButton('submit', 
                                          attrs={'value': l_('Apply')}))


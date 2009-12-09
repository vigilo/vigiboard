# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Le formulaire d'édition d'un événement."""

from pylons.i18n import lazy_ugettext as l_
from tw.forms import TableForm, SingleSelectField, TextField, HiddenField
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
    class fields(WidgetsList):
        id = HiddenField()
        trouble_ticket = TextField(label_text=l_('Trouble Ticket'))
        ack = SingleSelectField(label_text=l_('Status'),
                    options=edit_event_status_options)

    submit_text = l_('Apply')


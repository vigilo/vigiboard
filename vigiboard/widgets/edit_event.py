# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Le formulaire d'édition d'un événement."""

import tg
from pylons.i18n import lazy_ugettext as l_
from tw.api import WidgetsList
from tw.forms import TableForm, SingleSelectField, TextField, \
                        HiddenField, Label

__all__ = (
    'edit_event_status_options',
    'EditEventForm',
)

edit_event_status_options = [
    ['NoChange', l_('No change')],
    ['None', l_('Change to None')],
    ['Acknowledged', l_('Change to Acknowledged')],
    ['AAClosed', l_('Change to Closed')],
    ['Forced', l_('Force to Closed')],
]

class EditEventForm(TableForm):
    """
    Formulaire d'édition d'événement

    Affiche une zone de texte pour le Trouble Ticket et une
    liste déroulante pour le nouveau status

    Ce widget permet de répondre aux exigences suivantes :
        - VIGILO_EXIG_VIGILO_BAC_0060
        - VIGILO_EXIG_VIGILO_BAC_0110
    """

    class fields(WidgetsList):
        id = HiddenField('id')
        trouble_ticket = TextField(label_text=l_('Trouble Ticket'))
        warning = Label(suppress_label=True, text=l_('Warning: changing '
                        'the ticket will affect all selected events.'))
        ack = SingleSelectField(label_text=l_('Acknowledgement Status'),
                                options=edit_event_status_options)
        last_modification = HiddenField()


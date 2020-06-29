# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2020 CS GROUP – France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Le formulaire d'édition d'un événement."""

from tg.i18n import lazy_ugettext as l_
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

# Énumère les valeurs possibles pour le champ "type_action"
# dans la base de données et les marque comme nécessitant une traduction.
valid_action_types = {
    u'Ticket change': l_('Ticket change'),
    u'Forced change state': l_('Forced change state'),
    u'Acknowledgement change state': l_('Acknowledgement change state'),
    u'Ticket change notification': l_('Ticket change notification'),
    u'New occurrence': l_('New occurrence'),
    u'Nagios update state': l_('Nagios update state'),
}

# Gère le cas où un événement est clos de force.
l_('Forced')


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
        """
        Champs du formulaire d'édition des événements.
        """
        id = HiddenField('id')
        trouble_ticket = TextField(label_text=l_('Trouble Ticket'),
                                   maxlength=250)
        warning = Label(suppress_label=True, text=l_('Warning: changing '
                        'the ticket will affect all selected events.'))
        ack = SingleSelectField(label_text=l_('Acknowledgement Status'),
                                options=edit_event_status_options)
        last_modification = HiddenField()

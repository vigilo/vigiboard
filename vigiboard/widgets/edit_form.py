# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Le formulaire d'édition d'un événement."""

import tg
from tg.i18n import lazy_ugettext as l_
import tw2.forms as twf
from formencode import validators

__all__ = (
    'edit_event_status_options',
    'EditForm',
)

edit_event_status_options = [
    ['NoChange', l_('No change')],
    ['Unack', l_('Change to None')],
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


class EditForm(twf.TableForm):
    """
    Formulaire d'édition d'événement

    Affiche une zone de texte pour le Trouble Ticket et une
    liste déroulante pour le nouveau status

    Ce widget permet de répondre aux exigences suivantes :
        - VIGILO_EXIG_VIGILO_BAC_0060
        - VIGILO_EXIG_VIGILO_BAC_0110
    """
    action = tg.lurl('/update')
    submit = twf.SubmitButton(value=l_('Apply'))
    id = 'edit_event_form'

    # Champs du formulaire
    ids = twf.HiddenField(validator=validators.Regex(r'^[0-9]+(,[0-9]+)*,?$'))
    trouble_ticket = twf.TextField(label=l_('Trouble Ticket'),
                                   maxlength=250,
                                   validator=validators.UnicodeString(if_missing=''))
    ack = twf.SingleSelectField(label=l_('Acknowledgement Status'),
                                options=edit_event_status_options,
                                prompt_text=None)
    warning = twf.Label('warning', text=l_('Warning: all selected events '
                                           'will be impacted by the change.'))
    last_modification = twf.HiddenField(validator=validators.Number(not_empty=True))

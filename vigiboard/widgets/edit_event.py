# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
################################################################################
#
# Copyright (C) 2007-2009 CS-SI
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
################################################################################

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

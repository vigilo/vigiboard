# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Le formulaire de recherche/filtrage."""

from pylons.i18n import lazy_ugettext as l_
from tw.forms import TableForm, TextField, CalendarDateTimePicker, SubmitButton
from tw.api import WidgetsList
from tg import url

__all__ = ('SearchForm', )

class SearchForm(TableForm):
    """
    Formulaire de recherche dans les événements

    Affiche un champ texte pour l'hôte, le service, la sortie,
    le ticket d'incidence, et la date.
    """
        
    method = 'GET'
    style = 'display: none'
    submit_text = None
    action = './'
    fields = [
        TextField('hostgroup', label_text=l_('Host group')),
        TextField('servicegroup', label_text=l_('Service group')),
        TextField('host', label_text=l_('Host')),
        TextField('service', label_text=l_('Service')),
        TextField('output', label_text=l_('Output')),
        TextField('trouble_ticket', label_text=l_('Trouble Ticket'))
    ]
    
    def __init__(self,  id, lang, date_format='%Y-%m-%d %I:%M:%S %P', 
                 *args, **kwargs):
        super(SearchForm, self).__init__(id, *args, **kwargs)

        self.children.append(CalendarDateTimePicker(id + '_from_date', 
                                name = 'from_date',
                                label_text = l_('From'),
                                button_text = l_("Choose"),
                                date_format = date_format, 
                                not_empty = False,
                                calendar_lang=lang))
        
        self.children.append(CalendarDateTimePicker(id + '_to_date',
                                name = 'to_date',
                                label_text = l_('To'),
                                button_text = l_("Choose"),
                                date_format = date_format, 
                                not_empty = False,
                                calendar_lang=lang))

        self.children.append(SubmitButton('search',
                                          attrs={'value':l_('Search')}))


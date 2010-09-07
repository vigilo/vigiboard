# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Le formulaire de recherche/filtrage."""

from pylons.i18n import lazy_ugettext as l_
from tw.api import WidgetsList
import tw.forms as twf
from tg.i18n import get_lang
import tg

from vigilo.models.session import DBSession
from vigilo.models.tables.group import Group

__all__ = (
    'SearchForm',
    'create_search_form',
)

class GroupSelector(twf.InputField):
    params = ["choose_text", "text_value", "clear_text"]
    choose_text = l_('Choose')
    clear_text = l_('Clear')
    text_value = ''

    template = """
<div xmlns="http://www.w3.org/1999/xhtml"
   xmlns:py="http://genshi.edgewall.org/" py:strip="">
<input type="hidden" name="${name}" class="${css_class}"
    id="${id}.value" value="${value}" py:attrs="attrs" />
<input type="text" class="${css_class}" id="${id}.ui"
    value="${text_value}" readonly="readonly" py:attrs="attrs" />
<input type="button" class="${css_class}" id="${id}"
    value="${choose_text}" py:attrs="attrs" />
<input type="button" class="${css_class}" id="${id}.clear"
    value="${clear_text}" py:attrs="attrs" />
</div>
"""

    def update_params(self, d):
        super(GroupSelector, self).update_params(d)
        text_value = DBSession.query(Group.name).filter(
                        Group.idgroup == d.value).scalar()
        if not text_value:
            d.value = ''
        else:
            d.text_value = text_value

class SearchForm(twf.TableForm):
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
        supitemgroup = GroupSelector(label_text=l_('Group'))
        host = twf.TextField(label_text=l_('Host'))
        service = twf.TextField(label_text=l_('Service'))
        output = twf.TextField(label_text=l_('Output'))
        trouble_ticket = twf.TextField(label_text=l_('Trouble Ticket'))
        from_date = twf.CalendarDateTimePicker(
            label_text = l_('From'),
            button_text = l_("Choose"),
            not_empty = False)
        to_date = twf.CalendarDateTimePicker(
            label_text = l_('To'),
            button_text = l_("Choose"),
            not_empty = False)

def get_calendar_lang():
    # TODO: Utiliser le champ "language" du modèle pour cet utilisateur ?
    # On récupère la langue du navigateur de l'utilisateur
    lang = get_lang()
    if not lang:
        lang = tg.config['lang']
    else:
        lang = lang[0]

    # TODO: Il faudrait gérer les cas où tout nous intéresse dans "lang".
    # Si l'identifiant de langage est composé (ex: "fr_FR"),
    # on ne récupère que la 1ère partie.
    lang = lang.replace('_', '-')
    lang = lang.split('-')[0]
    return lang

create_search_form = SearchForm("search_form",
    submit_text=l_('Search'), action=tg.url('/'),
)


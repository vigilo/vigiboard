# -*- coding: utf-8 -*-
# Copyright (C) 2006-2020 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Validateur et convertisseur de dates selon un format.
"""
from formencode.api import FancyValidator, Invalid
from datetime import datetime

from tg.i18n import ugettext as _, get_lang

def get_calendar_lang():
    import tg

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

def get_date_format():
    # @HACK: nécessaire car l_() retourne un object LazyString
    # qui n'est pas sérialisable en JSON.
    # TRANSLATORS: Format de date et heure Python/JavaScript.
    # TRANSLATORS: http://www.dynarch.com/static/jscalendar-1.0/doc/html/reference.html#node_sec_5.3.5
    # TRANSLATORS: http://docs.python.org/release/2.5/lib/module-time.html
    return _('%Y-%m-%d %I:%M:%S %p').encode('utf-8')

class DateFormatConverter(FancyValidator):
    """
    Valide une date selon un format identique à ceux
    acceptés par la fonction strptime().
    """
    messages = {
        'invalid': 'Invalid value',
    }

    def _to_python(self, value, state):
        if not isinstance(value, basestring):
            raise Invalid(self.message('invalid', state), value, state)

        str_date = value.lower()
        if isinstance(str_date, unicode):
            str_date = str_date.encode('utf-8')

        try:
            # On tente d'interpréter la saisie de l'utilisateur
            # selon un format date + heure.
            date = datetime.strptime(str_date, get_date_format())
        except ValueError:
            try:
                # 2è essai : on essaye d'interpréter uniquement une date.
                # TRANSLATORS: Format de date Python/JavaScript.
                # TRANSLATORS: http://www.dynarch.com/static/jscalendar-1.0/doc/html/reference.html#node_sec_5.3.5
                # TRANSLATORS: http://docs.python.org/release/2.5/lib/module-time.html
                date = datetime.strptime(str_date, _('%Y-%m-%d').encode('utf8'))
            except ValueError:
                raise Invalid(self.message('invalid', state), value, state)
        return date

    def _from_python(self, value, state):
        if not isinstance(value, datetime):
            raise Invalid(self.message('invalid', state), value, state)

        # Même format que pour _to_python.
        return datetime.strftime(value, get_date_format()).decode('utf-8')

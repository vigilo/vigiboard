# -*- coding: utf-8 -*-
# Copyright (C) 2006-2011 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Validateur et convertisseur de dates selon un format.
"""
from formencode.api import FancyValidator, Invalid
from datetime import datetime

from pylons.i18n import ugettext as _

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
            # TRANSLATORS: Format de date et heure Python/JavaScript.
            # TRANSLATORS: http://www.dynarch.com/static/jscalendar-1.0/doc/html/reference.html#node_sec_5.3.5
            # TRANSLATORS: http://docs.python.org/release/2.5/lib/module-time.html
            date = datetime.strptime(str_date, _('%Y-%m-%d %I:%M:%S %p').encode('utf8'))
        except ValueError:
            raise Invalid(self.message('invalid', state), value, state)
        return date

    def _from_python(self, value, state):
        if not isinstance(value, datetime):
            raise Invalid(self.message('invalid', state), value, state)

        # Même format que pour _to_python.
        return datetime.strftime(
                    value,
                    _('%Y-%m-%d %I:%M:%S %p').encode('utf8')
                ).decode('utf-8')

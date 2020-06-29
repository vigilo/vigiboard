# -*- coding: utf-8 -*-
# Copyright (C) 2006-2020 CS GROUP – France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Sample controller module"""

import logging
from tg import expose, response
from datetime import datetime

from vigilo.turbogears.controllers import BaseController

LOGGER = logging.getLogger(__name__)

__all__ = ['FeedsController']

class FeedsController(BaseController):
    # pylint: disable-msg=R0201,W0613

    @expose('atom.xml')
    def atom(self, token, username):
        """
        """
        response.headers['Content-Type'] = 'application/atom+xml; charset=utf-8'
        return {
            'feed': {
                'title': 'VigiBoard',
                'mtime': datetime.utcnow(),
            },
            'entries': [
                {
                    'title': 'Test',
                    'mtime': datetime.utcnow(),
                    'summary': 'Foo bar on baz',
                }
            ],
        }

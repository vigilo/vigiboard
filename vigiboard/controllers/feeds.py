# -*- coding: utf-8 -*-
# Copyright (C) 2006-2011 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Sample controller module"""

import logging
from tg import expose, response
from datetime import datetime
from tg.controllers import CUSTOM_CONTENT_TYPE

from vigilo.turbogears.controllers import BaseController

LOGGER = logging.getLogger(__name__)

__all__ = ['FeedsController']

class FeedsController(BaseController):
    # pylint: disable-msg=R0201,W0613

    @expose('atom.xml', content_type=CUSTOM_CONTENT_TYPE)
    def atom(self, token, username):
        """
        """
        response.headers['Content-Type'] = 'application/atom+xml; charset=utf-8'
        return {
            'feed': {
                'title': 'VigiBoard',
                'mtime': datetime.now(),
            },
            'entries': [
                {
                    'title': 'Test',
                    'mtime': datetime.now(),
                    'summary': 'Foo bar on baz',
                }
            ],
        }

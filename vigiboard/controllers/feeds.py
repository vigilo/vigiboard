# -*- coding: utf-8 -*-
"""Sample controller module"""

import logging
from tg import expose, redirect, config, request, response
from pylons.i18n import ugettext as _
from datetime import datetime
from repoze.what.predicates import Any, has_permission, in_group
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
        response.headers['Content-Type'] = 'application/atom+xml'
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

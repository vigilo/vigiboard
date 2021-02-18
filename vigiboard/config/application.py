# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
# Copyright (C) 2007-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""WSGI middleware initialization for the vigiboard application."""

import imp
import os.path
from pkg_resources import resource_filename
from tg.support.statics import StaticsMiddleware

__all__ = ['make_app']


def make_app(global_conf, **app_conf):
    """
    Set vigiboard up with the settings found in the PasteDeploy configuration
    file used.

    This is the PasteDeploy factory for the vigiboard application.

    C{app_conf} contains all the application-specific settings (those defined
    under ``[app:main]``).

    @param global_conf: The global settings for vigiboard (those
        defined under the ``[DEFAULT]`` section).
    @type global_conf: C{dict}
    @param full_stack: Should the whole TG2 stack be set up?
    @type full_stack: C{str} or C{bool}
    @return: The vigiboard application with all the relevant middleware
        loaded.
    """
    # Charge le fichier "app_cfg.py" se trouvant aux côtés de "settings.ini".
    mod_info = imp.find_module('app_cfg', [ global_conf['here'] ])
    app_cfg = imp.load_module('vigiboard.config.app_cfg', *mod_info)
    base_config = app_cfg.base_config

    # Initialisation de l'application et de son environnement d'exécution.
    app = base_config.make_wsgi_app(global_conf, app_conf, wrap_app=None)

    max_age = app_conf.get("cache_max_age")
    try:
        max_age = int(max_age)
    except (ValueError, TypeError):
        max_age = 0

    # Apply middleware for static files in reverse order
    # (user-supplied customizations override theme/application-provided files)
    app = StaticsMiddleware(app, resource_filename('vigiboard', 'public'), max_age)
    app = StaticsMiddleware(app, resource_filename('vigilo.themes.public', 'common'), max_age)
    app = StaticsMiddleware(app, resource_filename('vigilo.themes.public', 'vigiboard'), max_age)
    app = StaticsMiddleware(app, os.path.join(global_conf['here'], 'public'), max_age)
    return app

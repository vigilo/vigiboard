# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
################################################################################
#
# Copyright (C) 2007-2016 CS-SI
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

"""WSGI middleware initialization for the vigiboard application."""

import imp
import os.path
from pkg_resources import resource_filename
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser

__all__ = ['make_app']


def make_app(global_conf, full_stack=True, **app_conf):
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
    load_environment = base_config.make_load_environment()
    make_base_app = base_config.setup_tg_wsgi_app(load_environment)
    app = make_base_app(global_conf, full_stack=True, **app_conf)

    max_age = app_conf.get("cache_max_age")
    try:
        max_age = int(max_age)
    except (ValueError, TypeError):
        max_age = None

    # Personalisation des fichiers statiques via un dossier public/
    # dans le répertoire contenant le fichier settings.ini chargé.
    custom_static = StaticURLParser(os.path.join(global_conf['here'], 'public'),
                                    cache_max_age=max_age)

    # On définit 2 middlewares pour fichiers statiques qui cherchent
    # les fichiers dans le thème actuellement chargé.
    # Le premier va les chercher dans le dossier des fichiers spécifiques
    # à l'application, le second cherche dans les fichiers communs.
    app_static = StaticURLParser(
        resource_filename('vigilo.themes.public', 'vigiboard'),
        cache_max_age=max_age)
    common_static = StaticURLParser(
        resource_filename('vigilo.themes.public', 'common'),
        cache_max_age=max_age)
    local_static = StaticURLParser(
        resource_filename('vigiboard', 'public'),
        cache_max_age=max_age)
    app = Cascade([custom_static, app_static, common_static, local_static, app])
    return app

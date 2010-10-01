# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
################################################################################
#
# Copyright (C) 2007-2011 CS-SI
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

from vigiboard.config.app_cfg import base_config
from vigiboard.config.environment import load_environment

from pkg_resources import resource_filename
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser
from repoze.who.plugins.testutil import make_middleware_with_config \
                                    as make_who_with_config

__all__ = ['make_app']

# Use base_config to setup the necessary PasteDeploy application factory.
# make_base_app will wrap the TG2 app with all the middleware it needs.
make_base_app = base_config.setup_tg_wsgi_app(load_environment)


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
    app = make_base_app(global_conf, full_stack=full_stack, **app_conf)

    # On définit 2 middlewares pour fichiers statiques qui cherchent
    # les fichiers dans le thème actuellement chargé.
    # Le premier va les chercher dans le dossier des fichiers spécifiques
    # à l'application, le second cherche dans les fichiers communs.
    app_static = StaticURLParser(resource_filename(
        'vigilo.themes.public', 'vigiboard'))
    common_static = StaticURLParser(resource_filename(
        'vigilo.themes.public', 'common'))
    local_static = StaticURLParser(resource_filename(
                'vigiboard', 'public'))
    app = Cascade([app_static, common_static, local_static, app])

    app = make_who_with_config(
        app, global_conf,
        app_conf.get('auth.config', 'who.ini'),
        app_conf.get('auth.log_file', None),
        app_conf.get('auth.log_level', 'debug'),
        app_conf.get('skip_authentication')
    )
    return app

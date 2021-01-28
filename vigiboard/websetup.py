# -*- coding: utf-8 -*-
# Copyright (C) 2007-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Setup the vigiboard application"""

# pylint: disable-msg=W0613
# W0613: Unused arguments: on doit respecter l'API

import imp

__all__ = ['setup_app', 'populate_db']

def _(msg):
    """
    Cette fonction n'est jamais exécutée.
    Elle permet simplement de forcer la traduction de
    chaînes provenant de vigilo-turbogears
    """
    _('Vigilo has detected a breakdown on the following '
      'collector(s): %(list)s')

def setup_app(command, conf, variables):
    """Place any commands to setup vigiboard here"""
    from vigilo.turbogears import populate_db as tg_pop_db

    # Charge le fichier "app_cfg.py" se trouvant aux côtés de "settings.ini".
    mod_info = imp.find_module('app_cfg', [ conf.global_conf['here'] ])
    app_cfg = imp.load_module('vigiboard.config.app_cfg', *mod_info)

    # Initialisation de l'environnement d'exécution.
    load_environment = app_cfg.base_config.make_load_environment()
    load_environment(conf.global_conf, conf.local_conf)
    tg_pop_db()

def populate_db(bind):
    from vigilo.models.session import DBSession
    from vigilo.models import tables

    permissions = {
        'vigiboard-access':
            'Gives access to VigiBoard',

        'vigiboard-update':
            'Allows users to update events',

        'vigiboard-admin':
            'Allows users to forcefully close open events',

        'vigiboard-silence':
            'Allows users to view and edit silence rules',
    }

    for (permission_name, description) in permissions.iteritems():
        if not tables.Permission.by_permission_name(unicode(permission_name)):
            DBSession.add(tables.Permission(
                permission_name=unicode(permission_name),
                description=unicode(description),
            ))
    DBSession.flush()

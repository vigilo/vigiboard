# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
"""
Global configuration file for TG2-specific settings in vigiboard.

This file complements development/deployment.ini.

Please note that **all the argument values are strings**. If you want to
convert them into boolean, for example, you should use the
:func:`paste.deploy.converters.asbool` function, as in::
    
    from paste.deploy.converters import asbool
    setting = asbool(global_conf.get('the_setting'))
 
"""

from tg.configuration import AppConfig

class MyAppConfig(AppConfig):
    """We overload AppConfig for our needs."""

    def __init__(self, app_name):
        super(MyAppConfig, self).__init__()
        self.__app_name = app_name
        self.__tpl_translator = None

    def __setup_template_translator(self):
        from pkg_resources import resource_filename
        import gettext
        from tg.i18n import get_lang

        if self.__tpl_translator is None:
            i18n_dir = resource_filename('vigilo.themes', 'i18n')
            lang = get_lang()

            # During unit tests, no language is defined
            # which results in an error if gettext.translation
            # is used to retrieve translations.
            if lang is None:
                self.__tpl_translator = gettext.NullTranslations()
            else:                
                self.__tpl_translator = gettext.translation(
                    'theme', i18n_dir, get_lang())

    def setup_paths(self):
        """Add egg-aware search path to genshi."""
        super(MyAppConfig, self).setup_paths()
        from pkg_resources import resource_filename

        app_templates = resource_filename(
            'vigilo.themes.templates', self.__app_name)
        common_templates = resource_filename(
            'vigilo.themes.templates', 'common')
        self.paths['templates'] = [app_templates, common_templates]

    def setup_genshi_renderer(self):
        """Setup templates to use an alternate translator."""
        # On reprend plusieurs éléments de "tg.configuration".
        from genshi.template import TemplateLoader
        from genshi.filters import Translator
        from tg.render import render_genshi
        from pkg_resources import resource_filename
        from tg.configuration import config

        def template_loaded(template):
            """Called when a template is done loading."""
            self.__setup_template_translator()
            template.filters.insert(0, Translator(self.__tpl_translator.ugettext))

        def my_render_genshi(template_name, template_vars, **kwargs):
            self.__setup_template_translator()
            template_vars['l_'] = self.__tpl_translator.ugettext
            return render_genshi(template_name, template_vars, **kwargs)

        loader = TemplateLoader(search_path=self.paths.templates,
                                auto_reload=self.auto_reload_templates,
                                callback=template_loaded)

        config['pylons.app_globals'].genshi_loader = loader
        self.render_functions.genshi = my_render_genshi

    def setup_sqlalchemy(self):
        """
        TG2 needs to configure the DB session before anything else, then it
        calls init_model(). In our case, the DB session is already configured
        so the function call is unnecessary. We suppress TG2's behaviour here.
        """
        pass

import vigiboard
from vigiboard import model
from vigiboard.lib import app_globals, helpers

base_config = MyAppConfig('vigiboard')
base_config.renderers = []

# Pour gérer les thèmes, la notation "pointée" n'est pas utilisée.
# À la place, on indique le nom complet du template (ex: "index.html")
# lors de l'appel au décorateur @expose.
base_config.use_dotted_templatenames = False

# On définit la variable à False. En réalité, le comportement
# est le même que si elle valait toujours True, sauf que l'on
# met en place les middlewares nous même pour pouvoir gérer les
# thèmes (cf. ./middleware.py).
base_config.serve_static = False

base_config.package = vigiboard

#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi')
# if you want raw speed and have installed chameleon.genshi
# you should try to use this renderer instead.
# warning: for the moment chameleon does not handle i18n translations
#base_config.renderers.append('chameleon_genshi')

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = model
base_config.DBSession = model.DBSession

# Configure the authentication backend
base_config.auth_backend = 'sqlalchemy'
base_config.sa_auth.dbsession = model.DBSession
# what is the class you want to use to search for users in the database
base_config.sa_auth.user_class = model.User
# what is the class you want to use to search for groups in the database
base_config.sa_auth.group_class = model.UserGroup
# what is the class you want to use to search for permissions in the database
base_config.sa_auth.permission_class = model.Permission
# The name "groups" is already used for groups of hosts.
# We use "usergroups" when referering to users to avoid confusion.
base_config.sa_auth.translations.groups = 'usergroups'

# override this if you would like to provide a different who plugin for
# managing login and logout of your application
base_config.sa_auth.form_plugin = None

# You may optionally define a page where you want users to be redirected to
# on login:
base_config.sa_auth.post_login_url = '/post_login'

# You may optionally define a page where you want users to be redirected to
# on logout:
base_config.sa_auth.post_logout_url = '/post_logout'


##################################
# Settings specific to Vigiboard #
##################################

# Vigiboard version
base_config['vigiboard_version'] = u'0.1'

# Links configuration
# XXX Should be part of ini settings.
base_config['vigiboard_links.eventdetails'] = {
    'nagios': ['Nagios host details', 'http://example1.com/%(idaggregate)s'],
    'metrology': ['Metrology details', 'http://example2.com/%(idaggregate)s'],
    'security': ['Security details', 'http://example3.com/%(idaggregate)s'],
    'servicetype': ['Service Type', 'http://example4.com/%(idaggregate)s'],
}

# Plugins to use
# XXX Should be part of ini settings.
base_config['vigiboard_plugins'] = [
    ['shn', 'PluginSHN'],
]


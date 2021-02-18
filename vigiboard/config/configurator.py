# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
# Copyright (C) 2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

from pkg_resources import working_set
from vigilo.turbogears.configurator import Configurator

class VigiboardConfigurator(Configurator):
    def setup(self, conf):
        super(VigiboardConfigurator, self).setup(conf)

        # On est obligés d'attendre que la base de données
        # soit configurée pour pouvoir charger les plugins.
        from vigiboard.controllers.plugins import VigiboardRequestPlugin

        plugins = []
        for plugin_name in conf['vigiboard_plugins']:
            try:
                ep = working_set.iter_entry_points(
                        "vigiboard.columns", plugin_name).next()
            except StopIteration:
                pass

            if ep.name in dict(plugins):
                continue

            try:
                plugin_class = ep.load(require=True)
                if issubclass(plugin_class, VigiboardRequestPlugin):
                    plugins.append((unicode(ep.name), plugin_class()))
            except Exception: # pylint: disable-msg=W0703
                # W0703: Catch "Exception"
                LOGGER.exception(u'Unable to import plugin %s' % plugin_name)
        conf['columns_plugins'] = plugins


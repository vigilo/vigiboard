#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

import os
from setuptools import setup, find_packages

setup_requires = ['vigilo-common'] if not os.environ.get('CI') else []

cmdclass = {}
try:
    from vigilo.common.commands import compile_catalog_plusjs
    cmdclass['compile_catalog'] = compile_catalog_plusjs
except ImportError:
    pass

tests_require = [
    'WebTest',
    'lxml',
    'coverage',
    'gearbox',
]


setup(
    name='vigilo-vigiboard',
    version='5.2.0',
    author='Vigilo Team',
    author_email='contact.vigilo@csgroup.eu',
    zip_safe=False, # pour pouvoir déplacer app_cfg.py
    license='http://www.gnu.org/licenses/gpl-2.0.html',
    description="Vigilo event board",
    long_description="Vigilo event board",
    url='https://www.vigilo-nms.com/',
    setup_requires=setup_requires,
    install_requires=[
        "vigilo-turbogears",
    ],
    packages=find_packages(),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=tests_require,
    extras_require={
        'tests': tests_require,
    },
    package_data={
        'vigiboard': [
            'i18n/*/LC_MESSAGES/*.mo',
            'i18n/*/LC_MESSAGES/*.js',
            'templates/*/*',
            'public/js/*.js',
        ],
    },
    message_extractors={
        'vigiboard': [
            ('**.py', 'python', None),
            ('**/public/js/*.js', 'javascript', None),
        ],
    },

    entry_points={
        'paste.app_factory': [
            'main = vigiboard.config.middleware:make_app',
        ],
        'vigilo.models': [
            'populate_db = vigiboard.websetup:populate_db',
        ],
        'vigiboard.columns': [
            'id = vigiboard.controllers.plugins.id:PluginId',
            'test = vigiboard.controllers.plugins.test:PluginTest',
            'details = vigiboard.controllers.plugins.details:PluginDetails',
            'date = vigiboard.controllers.plugins.date:PluginDate',
            'priority = vigiboard.controllers.plugins.priority:PluginPriority',
            'occurrences = vigiboard.controllers.plugins.occurrences:PluginOccurrences',
            'address = vigiboard.controllers.plugins.address:PluginAddress',
            'hostname = vigiboard.controllers.plugins.hostname:PluginHostname',
            'servicename = vigiboard.controllers.plugins.servicename:PluginServicename',
            'output = vigiboard.controllers.plugins.output:PluginOutput',
            'hls = vigiboard.controllers.plugins.hls:PluginHLS',
            'state = vigiboard.controllers.plugins.state:PluginState',
            'status = vigiboard.controllers.plugins.status:PluginStatus',
            'groups = vigiboard.controllers.plugins.groups:PluginGroups',
            'masked_events = vigiboard.controllers.plugins.masked_events:PluginMaskedEvents',
            'map = vigiboard.controllers.plugins.map:PluginMap',
        ],
        'vigilo.turbogears.i18n': [
            'vigiboard = vigiboard.i18n:100',
        ],
    },
    cmdclass=cmdclass,
    vigilo_build_vars={
        'nagios': {
            'default': '/nagios/',
            'description': "URL to Nagios' UI relative to the webserver's root",
        },
        'sysconfdir': {
            'default': '/etc',
            'description': "installation directory for configuration files",
        },
        'localstatedir': {
            'default': '/var',
            'description': "local state directory",
        },
    },
    data_files=[
        ('@sysconfdir@/logrotate.d', ['deployment/vigilo-vigiboard.in']),
        (os.path.join('@sysconfdir@', 'vigilo', 'vigiboard'), [
            'deployment/vigiboard.wsgi.in',
            'deployment/vigiboard.conf.in',
            'deployment/settings.ini.in',
            'deployment/who.ini',
            'app_cfg.py',
        ]),
        (os.path.join("@localstatedir@", "log", "vigilo", "vigiboard"), []),
        (os.path.join("@localstatedir@", "cache", "vigilo", "sessions"), []),
    ],
)

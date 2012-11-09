#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2012 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

tests_require = [
    'WebTest',
    'BeautifulSoup',
    'lxml',
    'coverage',
]

sysconfdir = os.getenv("SYSCONFDIR", "/etc")

cmdclass = {}
try:
    from babeljs import compile_catalog_plusjs
except ImportError:
    pass
else:
    cmdclass['compile_catalog'] = compile_catalog_plusjs

setup(
    name='vigilo-vigiboard',
    version='3.0.0',
    author='Vigilo Team',
    author_email='contact@projet-vigilo.org',
    zip_safe=False, # pour pouvoir déplacer app_cfg.py
    license='http://www.gnu.org/licenses/gpl-2.0.html',
    description="Vigilo event board",
    long_description="Vigilo event board",
    url='http://www.projet-vigilo.org/',
    install_requires=[
        "vigilo-turbogears",
        "tw.forms",
    ],

    packages=find_packages(exclude=['ez_setup']),
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
        'paste.app_install': [
            'main = pylons.util:PylonsInstaller',
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
            'hostname = vigiboard.controllers.plugins.hostname:PluginHostname',
            'servicename = vigiboard.controllers.plugins.servicename:PluginServicename',
            'output = vigiboard.controllers.plugins.output:PluginOutput',
            'hls = vigiboard.controllers.plugins.hls:PluginHLS',
            'status = vigiboard.controllers.plugins.status:PluginStatus',
            'groups = vigiboard.controllers.plugins.groups:PluginGroups',
            'masked_events = vigiboard.controllers.plugins.masked_events:PluginMaskedEvents',
        ]
    },
    cmdclass=cmdclass,
    data_files=[
        (os.path.join(sysconfdir, 'vigilo/vigiboard/'), [
            'deployment/vigiboard.conf',
            'deployment/vigiboard.wsgi',
            'deployment/settings.ini',
            'deployment/who.ini',
        ]),
    ],
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:

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

setup(
    name='vigiboard',
    version='2.0.0',
    description='IHM Module for the Dashboard',
    author='Vigilo Team',
    author_email='contact@projet-vigilo.org',
    zip_safe=False,
    license='http://www.gnu.org/licenses/gpl-2.0.html',
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
        ],
    },
    message_extractors={
        'vigiboard': [
            ('**.py', 'python', None),
        ],
        '../turbogears/src': [
            ('**.py', 'python', None),
        ],
    },

    entry_points={
        'paste.app_factory': [
            'main = vigiboard.config.middleware:make_app',
        ],
        'paste.app_install': [
            'main = pylons.util:PylonsInstaller',
        ],
        'console_scripts': [
            'vigiboard-init-db = vigiboard.websetup:init_db',
        ],
    },
    data_files=[
        (os.path.join(sysconfdir, 'vigilo/vigiboard/'), [
            'deployment/vigiboard.conf',
            'deployment/vigiboard.wsgi',
            'deployment/settings.ini',
        ]),
    ],
)


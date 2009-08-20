# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

tests_require = ['WebTest', 'BeautifulSoup']

setup(
    name='vigiboard',
    version='0.1',
    description="""
    IHM Module for the Dashboard
    """,
    author="""Thomas ANDREJAK""",
    author_email="""thomas.andrejak@gmail.com""",
    install_requires=[
        "TurboGears2 >= 2.0b7",
        "Catwalk >= 2.0.2",
        "Babel >=0.9.4",
        "ToscaWidgets >= 0.9.7.1",
        "zope.sqlalchemy >= 0.4 ",
        "repoze.tm2 >= 1.0a4",
        "repoze.what-quickstart >= 1.0",
        "psycopg2",
        "tw.jquery >= 0.9.5",
        "vigilo-models",
        "PasteScript >= 1.7", # setup_requires has issues
        "decorator != 3.1.0", # Blacklist bad version
        ],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=tests_require,
    extras_require={
        'tests': tests_require,
        },
    package_data={'vigiboard': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    message_extractors={'vigiboard': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points={
        'paste.app_factory': [
            'main = vigiboard.config.middleware:make_app',
            ],
        'paste.app_install': [
            'main = pylons.util:PylonsInstaller',
            ],
        'console_scripts': [
            'runtests-vigiboard = vigiboard.tests:runtests [tests]',
            ],
        },
)


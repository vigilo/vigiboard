# -*- coding: utf-8 -*-
# Copyright (C) 2011-2019 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

name = u'vigiboard'

name = u'vigiboard'

project = u'VigiBoard'

pdf_documents = [
        ('admin', "admin-%s" % name, u"%s : Guide d'administration" % project, u'Vigilo'),
        ('dev', "dev-%s" % name, u"%s : Guide de développement" % project, u'Vigilo'),
        ('util', "util-%s" % name, u"%s : Guide d'utilisation" % project, u'Vigilo'),
]

latex_documents = [
        ('admin', 'admin-%s.tex' % name, u"%s : Guide d'administration" % project,
         'AA100004-2/ADM00005', 'vigilo'),
        ('dev', 'dev-%s.tex' % name, u"%s : Guide de développement" % project,
         'AA100004-2/DEV00002', 'vigilo'),
        ('util', 'util-%s.tex' % name, u"%s : Guide d'utilisation" % project,
         'AA100004-2/UTI00002', 'vigilo'),
]

execfile("../buildenv/doc/conf.py")

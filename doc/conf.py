# -*- coding: utf-8 -*-

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

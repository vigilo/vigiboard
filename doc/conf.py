# -*- coding: utf-8 -*-

name = u'vigiboard'

project = u'VigiBoard'

pdf_documents = [
        ('admin', "admin-%s" % name, "%s : Guide d'administration" % project, u'Vigilo'),
]

latex_documents = [
        ('admin', 'admin-%s.tex' % name, u"%s : Guide d'administration" % project,
         'AA100004-2/ADM00005', 'vigilo'),
]

execfile("../buildenv/doc/conf.py")

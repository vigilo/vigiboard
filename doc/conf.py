# -*- coding: utf-8 -*-

project = u'VigiBoard'

pdf_documents = [
        ('admin', "admin-vigiboard", "VigiBoard : Guide d'administration", u'Vigilo'),
]

latex_documents = [
        ('admin', 'admin-vigiboard.tex', u"VigiBoard : Guide d'administration",
         'AA100004-2/ADM00005', 'vigilo'),
]

execfile("../buildenv/doc/conf.py")

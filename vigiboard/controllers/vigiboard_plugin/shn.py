# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 

from vigiboard.controllers.vigiboard_plugin import \
        VigiboardRequestPlugin
from vigiboard.model import DBSession, ServiceHautNiveau, Events, Service
from sqlalchemy import sql, asc
from pylons.i18n import ugettext as _
from tg import tmpl_context,config,url
from tw.jquery.ui_dialog import JQueryUIDialog

class PluginSHN (VigiboardRequestPlugin):

    """
    Plugin permettant de rajouter le nombre de SHNs impactés à
    l'affichage
    """

    def __init__(self):
        super(PluginSHN,self).__init__(
            table = [ServiceHautNiveau.servicename_dep,
                sql.func.count(Events.idevent)],
            outerjoin = [(ServiceHautNiveau,
                ServiceHautNiveau.servicename_dep == Events.servicename)],
            groupby = [(Events),(ServiceHautNiveau.servicename_dep)],
            name = _(u'SHNs impacté'),
            style = {'style':'text-align:center'},
            object_name = "shn"
        )
    
    def show(self, req):
        """Fonction d'affichage"""
        if req[1] :
            return '<a href="javascript:vigiboard_shndialog(\'%s\',\'%d\')" class="SHNLien">%s</a>' % (url(''), req[0].idevent, req[2])
        else :
            return ""

    def context(self,context):
        """Fonction de context"""

        tmpl_context.shndialog = JQueryUIDialog(id='SHNDialog',
                autoOpen=False,title='%s%s' % (_('Service de haut niveau'),'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'))
        context.append([tmpl_context.shndialog,self.object_name])

    def controller(self,*argv,**krgv):
        idevent = krgv['idevent']
        e = DBSession.query(Events.servicename).filter(Events.idevent == idevent)
        s = e.one().servicename
        e = DBSession.query(ServiceHautNiveau.servicename).filter(ServiceHautNiveau.servicename_dep == s)
        return dict( shns = [ee.servicename for ee in e]) 


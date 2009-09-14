# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""
Plugin SHN : High level service
"""

from vigiboard.controllers.vigiboard_plugin import \
        VigiboardRequestPlugin
from vigiboard.model import DBSession, ServiceHautNiveau, Event
from sqlalchemy import sql
from pylons.i18n import gettext as _
from tg import tmpl_context, url
from tw.jquery.ui_dialog import JQueryUIDialog

class PluginSHN(VigiboardRequestPlugin):

    """
    Plugin permettant de rajouter le nombre de SHNs impactés à
    l'affichage
    """

    def __init__(self):
        super(PluginSHN, self).__init__(
            table = [ServiceHautNiveau.servicename_dep,
                sql.func.count(Event.idevent)],
            outerjoin = [(ServiceHautNiveau,
                ServiceHautNiveau.servicename_dep == Event.servicename)],
            groupby = [(Event),(ServiceHautNiveau.servicename_dep)],
            name = _(u'Impacted HLS'),
            style = {'title': _(u'Impacted High-Level Services'),
                'style': 'text-align:center'},
            object_name = "shn"
        )
    
    def show(self, req):
        """Fonction d'affichage"""
        if not req[1] is None:
            dico = {
                'baseurl': url(''),
                'idevent': req[0].idevent,
                'impacted_hls': req[2],
            }
            return '<a href="javascript:vigiboard_shndialog(\'%(baseurl)s\','\
                    '\'%(idevent)d\')" class="SHNLien">%(impacted_hls)d</a>' % \
                    dico
        else:
            return ""

    def context(self, context):
        """Fonction de context"""

        # XXX We insert 10 unbreakable spaces (&#160;) to workaround a bug
        # in JQuery where the dialog's width is incorrectly set.
        tmpl_context.shndialog = JQueryUIDialog(id='SHNDialog',
                autoOpen=False, title='%s%s' % (_(u'High-Level Service'),
                '&#160;' * 10))
        context.append([tmpl_context.shndialog, self.object_name])

    def controller(self, *argv, **krgv):
        """Ajout de fonctionnalités au contrôleur"""
        idevent = krgv['idevent']
        service = DBSession.query(Event.servicename
                ).filter(Event.idevent == idevent).one().servicename

        shns = DBSession.query(ServiceHautNiveau.servicename
                ).filter(ServiceHautNiveau.servicename_dep == service)
        return dict( shns = [shn.servicename for shn in shns]) 


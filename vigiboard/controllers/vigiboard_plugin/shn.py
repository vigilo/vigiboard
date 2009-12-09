# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""
Plugin SHN : High level service
"""

from vigiboard.controllers.vigiboard_plugin import \
        VigiboardRequestPlugin
from vigiboard.model import DBSession, CorrEvent
from pylons.i18n import gettext as _
from tg import url

class PluginSHN(VigiboardRequestPlugin):

    """
    Plugin permettant de rajouter le nombre de SHNs impactés à
    l'affichage et d'obtenir une liste détaillée de ces SHNs.
    """

    def __init__(self):
        super(PluginSHN, self).__init__(
            name = _(u'Impacted HLS'),
            style = {'title': _(u'Impacted High-Level Services'),
                'style': 'text-align:center'},
            object_name = "shn"
        )
    
    def show(self, aggregate):
        """Fonction d'affichage"""
        dico = {
            'baseurl': url('/'),
            'idcorrevent': aggregate.idcorrevent,
            'impacted_hls': aggregate.high_level_services.count(),
        }
        # XXX Il faudrait échapper l'URL contenue dans baseurl
        # pour éviter des attaques de type XSS.
        res = ('<a href="javascript:vigiboard_hls_dialog(this,' + \
                '\'%(baseurl)s\',%(idcorrevent)d)" ' + \
                'class="hls_link">%(impacted_hls)d</a>') % dico
        return res

    def context(self, context):
        """Fonction de context"""
        context.append([None, self.object_name])

    def controller(self, *argv, **krgv):
        """Ajout de fonctionnalités au contrôleur"""
        idcorrevent = krgv['idcorrevent']
        correvent = DBSession.query(CorrEvent) \
                .filter(CorrEvent.idcorrevent == idcorrevent).one()
        services = correvent.high_level_services

        return dict(services=[service.servicename for service in services])


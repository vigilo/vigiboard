# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""
Plugin SHN : High level service
"""

from pylons.i18n import ugettext as _
from tg import url

from vigiboard.controllers.vigiboard_plugin import VigiboardRequestPlugin
from vigilo.models.configure import DBSession
from vigilo.models import HighLevelService, \
                            CorrEvent, Event, SupItem

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
        supitem = DBSession.query(SupItem).join(
            (Event, Event.idsupitem == SupItem.idsupitem),
            (CorrEvent, CorrEvent.idcause == Event.idevent),
        ).filter(CorrEvent.idcorrevent == aggregate.idcorrevent).first()

        if not supitem:
            count = 0
        else:
            count = supitem.impacted_hls(
                HighLevelService.idservice
            ).count()

        dico = {
            'baseurl': url('/'),
            'idcorrevent': aggregate.idcorrevent,
            'count': count,
        }

        # XXX Il faudrait échapper l'URL contenue dans baseurl
        # pour éviter des attaques de type XSS.
        res = ('<a href="javascript:vigiboard_hls_dialog(this,' + \
                '\'%(baseurl)s\',%(idcorrevent)d)" ' + \
                'class="hls_link">%(count)d</a>') % dico
        return res

    def context(self, context):
        """Fonction de context"""
        context.append([None, self.object_name])

    def controller(self, idcorrevent, *argv, **krgv):
        """Ajout de fonctionnalités au contrôleur"""
        supitem = self.get_correvent_supitem(idcorrevent)

        if not supitem:
            # XXX On devrait afficher une erreur (avec tg.flash()).
            return []

        services = supitem.impacted_hls(
            HighLevelService.servicename
        ).order_by(
            HighLevelService.servicename.asc()
        ).all()

        return dict(services=[service.servicename for service in services])

    def get_correvent_supitem(self, idcorrevent):
        """
        Retourne le supitem ayant causé l'évènement 
        corrélé dont l'identifiant est passé en paramètre.
        """
        # On récupère l'item recherché dans la BDD
        supitem = DBSession.query(SupItem
            ).join(
                (Event, Event.idsupitem == SupItem.idsupitem),
                (CorrEvent, CorrEvent.idcause == Event.idevent),
            ).filter(CorrEvent.idcorrevent == idcorrevent).first()
            
#        # On détermine l'identité de l'utilisateur
#        username = request.environ['repoze.who.identity']['repoze.who.userid']
#        user = User.by_user_name(username)
#        
#        # On liste les permissions dont dispose l'utilisateur
#        user_permissions = []
#        for group in user.usergroups:
#            for permission in group.permissions:
#                user_permissions.append(permission)
#        
#        # On liste les permissions possibles pour l'item
#        supitem_permissions = []
#        for group in supitem.groups:
#            for permission in group.permissions:
#                supitem_permissions.append(permission)
#                
#        # On vérifie que l'utilisateur dispose bien des
#        # permissions sur l'item en question avant de le retourner.
#        for user_permission in user_permissions :
#            for supitem_permission in supitem_permissions :
#                if user_permission.idpermission == \
#                                            supitem_permission.idpermission:
#                    return supitem
#        
#        # Dans le cas contraire on retourne None
#        return None
    
        return supitem


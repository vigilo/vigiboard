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
            hls = None
        else:
            hls = supitem.impacted_hls(
                HighLevelService.servicename
            ).distinct().all()

        # Si aucun HLS n'est impacté, on n'affiche rien.
        if not hls:
            return ''

        # S'il n'y a qu'un seul HLS impacté,
        # on affiche directement son nom.
        if len(hls) == 1:
            return hls[0].servicename

        # Sinon, on affiche un lien permettant de récupérer
        # la liste de tous les HLS impactés. Le texte du lien
        # contient le nombre de HLS impactés.
        dico = {
            'baseurl': url('/'),
            'idcorrevent': aggregate.idcorrevent,
            'count': len(hls),
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
            return []

        services = supitem.impacted_hls(
            HighLevelService.servicename
        ).distinct().order_by(
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
        return supitem


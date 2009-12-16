# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""
Plugin SHN : High level service
"""

from pylons.i18n import gettext as _
from tg import url
from sqlalchemy.sql import functions

from vigiboard.controllers.vigiboard_plugin import \
        VigiboardRequestPlugin
from vigiboard.model import DBSession, ServiceHighLevel, \
                            CorrEvent, Event, \
                            ImpactedHLS, ImpactedPath
from vigilo.models.supitem import SupItem
from vigilo.models.secondary_tables import EVENTSAGGREGATE_TABLE

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
                ServiceHighLevel.idservice
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

    def controller(self, *argv, **krgv):
        """Ajout de fonctionnalités au contrôleur"""
        idcorrevent = krgv['idcorrevent']
        supitem = DBSession.query(SupItem).join(
            (Event, Event.idsupitem == SupItem.idsupitem),
            (CorrEvent, CorrEvent.idcause == Event.idevent),
        ).filter(CorrEvent.idcorrevent == idcorrevent).first()

        if not supitem:
            # XXX On devrait afficher une erreur (avec tg.flash()).
            return []

        services = supitem.impacted_hls(
            ServiceHighLevel.servicename
        ).order_by(
            ServiceHighLevel.servicename.asc()
        ).all()

        return dict(services=[service.servicename for service in services])


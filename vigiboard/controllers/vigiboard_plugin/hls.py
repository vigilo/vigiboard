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

class PluginHLS(VigiboardRequestPlugin):

    """
    Plugin permettant de rajouter le nombre de Service de Haut Niveau
    impactés à l'affichage et d'obtenir une liste détaillée de ces
    Services de Haut Niveau.
    """
    def get_value(self, idcorrevent):
        """Ajout de fonctionnalités au contrôleur"""
        supitem = self.get_correvent_supitem(idcorrevent)

        if not supitem:
            return []

        services = supitem.impacted_hls(
            HighLevelService.servicename
        ).distinct().order_by(
            HighLevelService.servicename.asc()
        ).all()

        return {'services': [service.servicename for service in services]}

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


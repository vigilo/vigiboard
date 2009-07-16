# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 

from vigiboard.controllers.vigiboard_ctl.vigiboard_plugin import \
        VigiboardRequestPlugin
from vigiboard.model import ServiceHautNiveau, Events
from sqlalchemy import sql, asc
from pylons.i18n import ugettext as _

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
            style = {'style':'text-align:center'}
        )
    
    def show(self, req):
        """Fonction d'affichage"""
        if req[1] :
            return req[2]
        else :
            return None

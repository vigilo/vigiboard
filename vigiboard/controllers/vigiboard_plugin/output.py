# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""
Un plugin pour VigiBoard qui ajoute une colonne avec la sortie
de la commande de test exécutée par Nagios sur cet hôte/service.
"""

from pylons.i18n import ugettext as _
from tg import url

from vigiboard.controllers.vigiboard_plugin import VigiboardRequestPlugin
from vigilo.models.configure import DBSession
from vigilo.models import HighLevelService, \
                            CorrEvent, Event, SupItem

class PluginOutput(VigiboardRequestPlugin):
    """Ajoute une colonne avec le message de Nagios."""


# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Un plugin pour VigiBoard qui ajoute une colonne avec le nom de l'hôte
sur lequel porte l'événement corrélé.
"""

from pylons.i18n import ugettext as _
from tg import url

from vigiboard.controllers.vigiboard_plugin import VigiboardRequestPlugin
from vigilo.models.configure import DBSession
from vigilo.models import HighLevelService, \
                            CorrEvent, Event, SupItem

class PluginHostname(VigiboardRequestPlugin):
    """
    Ajoute une colonne avec le nom de l'hôte impacté par un événement corrélé.
    """


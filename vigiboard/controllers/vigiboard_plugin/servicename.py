# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Un plugin pour VigiBoard qui ajoute une colonne avec le nom du service
à l'origine de l'événement corrélé.
"""

from pylons.i18n import ugettext as _
from tg import url

from vigiboard.controllers.vigiboard_plugin import VigiboardRequestPlugin
from vigilo.models.configure import DBSession
from vigilo.models import HighLevelService, \
                            CorrEvent, Event, SupItem

class PluginServicename(VigiboardRequestPlugin):
    """
    Affiche le nom du service à l'origine de l'événement corrélé.
    Si l'événement corrélé porte directement sur un hôte,
    alors le nom de service vaut None.
    """


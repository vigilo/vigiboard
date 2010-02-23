# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Un plugin pour VigiBoard qui ajoute une colonne avec l'identifiant
de l'événement corrélé.
Ce plugin n'a d'intérêt que pour débuguer l'application.
"""

from pylons.i18n import ugettext as _
from tg import url

from vigiboard.controllers.vigiboard_plugin import VigiboardRequestPlugin
from vigilo.models.configure import DBSession
from vigilo.models import HighLevelService, \
                            CorrEvent, Event, SupItem

class PluginId(VigiboardRequestPlugin):
    """Plugin de debug qui affiche l'identifiant de l'événement corrélé."""
    pass


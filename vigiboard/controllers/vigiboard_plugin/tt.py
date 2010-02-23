# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Un plugin pour VigiBoard qui ajoute une colonne avec un lien vers le ticket
d'incidence se rapportant à un événement corrélé donné.
"""

from pylons.i18n import ugettext as _
from tg import url

from vigiboard.controllers.vigiboard_plugin import VigiboardRequestPlugin
from vigilo.models.configure import DBSession
from vigilo.models import HighLevelService, \
                            CorrEvent, Event, SupItem

class PluginTroubleTicket(VigiboardRequestPlugin):
    """Ajoute un lien vers le ticket d'incidence associé à l'événement."""


# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Un plugin pour VigiBoard qui ajoute une colonne avec un lien vers le ticket
d'incidence se rapportant à un événement corrélé donné.
"""
from vigiboard.controllers.plugins import VigiboardRequestPlugin

class PluginTroubleTicket(VigiboardRequestPlugin):
    """Ajoute un lien vers le ticket d'incidence associé à l'événement."""


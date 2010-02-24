# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Un plugin pour VigiBoard qui ajoute une colonne avec le nom de l'hôte
sur lequel porte l'événement corrélé.
"""
from vigiboard.controllers.plugins import VigiboardRequestPlugin

class PluginHostname(VigiboardRequestPlugin):
    """
    Ajoute une colonne avec le nom de l'hôte impacté par un événement corrélé.
    """


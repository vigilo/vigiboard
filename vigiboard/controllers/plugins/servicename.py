# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Un plugin pour VigiBoard qui ajoute une colonne avec le nom du service
à l'origine de l'événement corrélé.
"""
from vigiboard.controllers.plugins import VigiboardRequestPlugin

class PluginServicename(VigiboardRequestPlugin):
    """
    Affiche le nom du service à l'origine de l'événement corrélé.
    Si l'événement corrélé porte directement sur un hôte,
    alors le nom de service vaut None.
    """


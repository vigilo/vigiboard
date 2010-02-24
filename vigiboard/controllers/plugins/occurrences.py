# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Un plugin pour VigiBoard qui ajoute une colonne avec le nombre
d'occurrences d'un événement corrélé donné.
"""
from vigiboard.controllers.plugins import VigiboardRequestPlugin

class PluginOccurrences(VigiboardRequestPlugin):
    """
    Ce plugin affiche le nombre d'occurrences d'un événement corrélé.
    Ce compteur d'occurrences est mis à jour automatiquement par le
    corrélateur chaque fois qu'un événement brut survient sur la cause
    de l'événement corrélé.
    """
    pass


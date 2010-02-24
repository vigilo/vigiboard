# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""
Un plugin pour VigiBoard qui ajoute une colonne avec la priorité
ITIL de l'événement corrélé.
"""
from vigiboard.controllers.plugins import VigiboardRequestPlugin

class PluginPriority(VigiboardRequestPlugin):
    """
    Ce plugin affiche la priorité ITIL des événements corrélés.
    La priorité est un nombre entier et permet de classer les événements
    corrélés dans l'ordre qui semble le plus approprié pour que les
    problèmes les plus urgents soient traités en premier.

    La priorité des événements peut être croissante (plus le nombre est
    élevé, plus il est urgent de traiter le problème) ou décroissante
    (ordre opposé). L'ordre utilisé par VigiBoard pour le tri est
    défini dans la variable de configuration C{vigiboard_priority_order}.
    """


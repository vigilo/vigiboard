# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2016 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Un plugin pour VigiBoard qui ajoute une colonne avec le nombre
d'occurrences d'un événement corrélé donné.
"""
from vigilo.models.tables import StateName, CorrEvent
from vigiboard.controllers.plugins import VigiboardRequestPlugin

class PluginOccurrences(VigiboardRequestPlugin):
    """
    Ce plugin affiche le nombre d'occurrences d'un événement corrélé.
    Ce compteur d'occurrences est mis à jour automatiquement par le
    corrélateur chaque fois qu'un événement brut survient sur la cause
    de l'événement corrélé.
    """
    def get_data(self, event):
        state = StateName.value_to_statename(event[0].cause.current_state)
        return {
            'state': state,
            'occurrences': event[0].occurrence,
        }

    def get_sort_criterion(self, query, column):
        if column == 'occurrences':
            return CorrEvent.occurrence
        return None


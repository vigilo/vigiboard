# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
################################################################################
#
# Copyright (C) 2007-2013 CS-SI
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
################################################################################

"""
Un plugin pour VigiBoard qui ajoute une colonne avec le nombre
d'occurrences d'un événement corrélé donné.
"""
from vigilo.models.tables import StateName
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

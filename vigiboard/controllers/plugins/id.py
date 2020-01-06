# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2020 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Un plugin pour VigiBoard qui ajoute une colonne avec l'identifiant
de l'événement corrélé.
Ce plugin n'a d'intérêt que pour débuguer l'application.
"""

from vigiboard.controllers.plugins import VigiboardRequestPlugin

class PluginId(VigiboardRequestPlugin):
    """Plugin de debug qui affiche l'identifiant de l'événement corrélé."""
    def get_data(self, event):
        return {
            'id': event[0].idcorrevent,
        }

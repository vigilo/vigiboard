# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Un plugin pour VigiBoard qui ajoute une colonne avec l'identifiant
de l'événement corrélé.
Ce plugin n'a d'intérêt que pour débuguer l'application.
"""

from vigiboard.controllers.plugins import VigiboardRequestPlugin

class PluginId(VigiboardRequestPlugin):
    """Plugin de debug qui affiche l'identifiant de l'événement corrélé."""
    pass


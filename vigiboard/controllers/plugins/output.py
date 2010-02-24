# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""
Un plugin pour VigiBoard qui ajoute une colonne avec la sortie
de la commande de test exécutée par Nagios sur cet hôte/service.
"""
from vigiboard.controllers.plugins import VigiboardRequestPlugin

class PluginOutput(VigiboardRequestPlugin):
    """Ajoute une colonne avec le message de Nagios."""


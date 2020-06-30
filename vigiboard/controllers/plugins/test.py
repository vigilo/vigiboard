# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2020 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Ce fichier contient un exemple de plugin pour l'interface
de VigiBoard. Il s'accompagne d'un template contenu dans
les thèmes, dans le répertoire suivant :
vigilo/themes/templates/vigiboard/plugins/test.html
"""
from vigiboard.controllers.plugins import VigiboardRequestPlugin

class PluginTest(VigiboardRequestPlugin):
    """
    Un plugin de démonstration qui se contente d'afficher
    "Hello world" pour chaque événement du tableau.
    """

    def get_bulk_data(self, events_ids):
        """
        Cette méthode est appelée par le L{RootController} de VigiBoard.
        Elle renvoie les données à afficher pour chaque évènement.

        @param events_ids: Liste des identifiants des événements corrélés
            à afficher.
        @type  events_ids: C{int}
        @return: Un dictionnaire associant à chaque identifiant d'évènement
            un texte statique.
        @rtype:  C{dict}
        """
        plugin_data = {}
        for event in events_ids:
            plugin_data[event] = 'Hello world'

        return plugin_data


# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
################################################################################
#
# Copyright (C) 2007-2014 CS-SI
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


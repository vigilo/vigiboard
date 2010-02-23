# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""
Ce fichier contient un exemple de plugin pour l'interface
de VigiBoard. Il s'accompagne d'un template contenu dans
les thèmes, dans le répertoire suivant :
vigilo/themes/templates/vigiboard/vigiboard_plugin/test.html
"""

from vigiboard.controllers.vigiboard_plugin import VigiboardRequestPlugin

class PluginTest(VigiboardRequestPlugin):
    """
    Un plugin de démonstration qui se contente d'afficher
    "Hello world" pour chaque événement du tableau.
    """

    def get_value(self, *args, **kwargs):
        """
        Cette méthode est appelée depuis le template associé à ce plugin,
        mais également lorsque l'on demande la valeur du plugin grâce à la
        méthode get_plugin_value du L{RootController} de VigiBoard.

        @param idcorrevent: Identifiant du L{CorrEvent} à interroger.
        @type idcorrevent: C{int}
        @return: Dictionnaire contenant un texte statique.
        @rtype: C{dict}
        """
        return {'text': 'Hello world'}


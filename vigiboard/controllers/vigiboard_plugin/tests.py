# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""
Plugin for tests
"""

from vigiboard.controllers.vigiboard_plugin.shn import \
	        PluginSHN
from vigiboard.model import EventHistory, Event

class MonPlugin(PluginSHN):
    """Plugin de test"""
    
    def __init__(self):
        PluginSHN.__init__(
            self,
            table = [EventHistory.idevent],
            join = [(EventHistory, EventHistory.idevent == Event.idevent)]
        )

    def show(self, req):
        """Fonction d'affichage"""
        return req[1]

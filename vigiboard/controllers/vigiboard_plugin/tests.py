# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""
Plugin for tests
"""

from vigiboard.controllers.vigiboard_plugin import \
        VigiboardRequestPlugin
from vigiboard.model import EventHistory, Event

class MonPlugin(VigiboardRequestPlugin):
    """Plugin de test"""
    
    def __init__(self):
        VigiboardRequestPlugin.__init__(
            self,
            table=[EventHistory.idevent],
            join=[(EventHistory, EventHistory.idevent == Event.idevent)],
            groupby=[EventHistory.idevent],
        )

    def show(self, aggregate):
        """Fonction d'affichage"""
        return aggregate


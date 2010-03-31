# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Un plugin pour VigiBoard qui ajoute une colonne avec la date à laquelle
est survenu un événement et la durée depuis laquelle l'événement est actif.
"""

from pylons.i18n import ugettext as _
from tg import url

from vigiboard.controllers.plugins import VigiboardRequestPlugin

class PluginDate(VigiboardRequestPlugin):
    """Plugin pour l'ajout d'une colonne Date."""
    pass


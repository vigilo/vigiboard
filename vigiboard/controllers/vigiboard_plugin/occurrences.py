# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Un plugin pour VigiBoard qui ajoute une colonne avec le nombre
d'occurrences d'un événement corrélé donné.
"""


from pylons.i18n import ugettext as _
from tg import url

from vigiboard.controllers.vigiboard_plugin import VigiboardRequestPlugin
from vigilo.models.configure import DBSession
from vigilo.models import HighLevelService, \
                            CorrEvent, Event, SupItem

class PluginOccurrences(VigiboardRequestPlugin):
    """
    Ce plugin affiche le nombre d'occurrences d'un événement corrélé.
    Ce compteur d'occurrences est mis à jour automatiquement par le
    corrélateur chaque fois qu'un événement brut survient sur la cause
    de l'événement corrélé.
    """
    pass


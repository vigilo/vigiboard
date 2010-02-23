# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Un plugin pour VigiBoard qui ajoute 3 colonnes au tableau des événements :
-   la première colonne contient l'état d'acquittement de l'événement.
-   la seconde colonne contient un lien permettant d'éditer certaines
    propriétés associées à l'événement corrélé.
-   la dernière colonne permet de (dé)sélectionner l'événement pour
    effectuer un traitement par lot.
"""

from pylons.i18n import ugettext as _
from tg import url

from vigiboard.controllers.vigiboard_plugin import VigiboardRequestPlugin
from vigilo.models.configure import DBSession
from vigilo.models import HighLevelService, \
                            CorrEvent, Event, SupItem

class PluginStatus(VigiboardRequestPlugin):
    """
    Ajoute des colonnes permettant de voir le statut d'acquittement
    d'un événement corrélé et de modifier certaines de ses propriétés.
    """

    def get_generated_columns_count(self):
        """
        Renvoie le nombre de colonnes que ce plugin ajoute.
        Ce plugin en ajoute 3, au lieu de 1 comme la plupart des plugins.
        """
        return 3


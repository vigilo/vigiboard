# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""
Un plugin pour VigiBoard qui ajoute une colonne avec la priorité
ITIL de l'événement corrélé.
"""

from pylons.i18n import ugettext as _
from tg import url

from vigiboard.controllers.vigiboard_plugin import VigiboardRequestPlugin
from vigilo.models.configure import DBSession
from vigilo.models import HighLevelService, \
                            CorrEvent, Event, SupItem

class PluginPriority(VigiboardRequestPlugin):
    """
    Ce plugin affiche la priorité ITIL des événements corrélés.
    La priorité est un nombre entier et permet de classer les événements
    corrélés dans l'ordre qui semble le plus approprié pour que les
    problèmes les plus urgents soient traités en premier.

    La priorité des événements peut être croissante (plus le nombre est
    élevé, plus il est urgent de traiter le problème) ou décroissante
    (ordre opposé). L'ordre utilisé par VigiBoard pour le tri est
    défini dans la variable de configuration C{vigiboard_priority_order}.
    """


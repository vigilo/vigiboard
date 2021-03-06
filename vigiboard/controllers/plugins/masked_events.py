# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2020 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Un plugin pour VigiBoard qui ajoute une colonne avec le nombre
d'événements masqués d'un événement corrélé.
"""
from sqlalchemy.sql import functions as func
from vigiboard.controllers.plugins import VigiboardRequestPlugin

from vigilo.models.session import DBSession
from vigilo.models.tables.secondary_tables import EVENTSAGGREGATE_TABLE

class PluginMaskedEvents(VigiboardRequestPlugin):
    """
    Affiche le nombre d'événements masqués par l'événement corrélé.
    """
    def get_bulk_data(self, events_ids):
        """
        Renvoie le nombre d'événements masqués par celui-ci.

        @param events_ids: Liste des identifiants des événements corrélés
            à afficher.
        @type events_ids: C{int}
        @return: Un dictionnaire associant à chaque identifiant d'évènement
            le nombre d'événements masqués.
        @rtype: C{dict}
        """
        counts = DBSession.query(
                func.count().label('masked'),
                EVENTSAGGREGATE_TABLE.c.idcorrevent
            ).group_by(EVENTSAGGREGATE_TABLE.c.idcorrevent
            ).filter(EVENTSAGGREGATE_TABLE.c.idcorrevent.in_(events_ids))

        res = {}
        for count in counts:
            # Il faut retirer la cause du décompte.
            res[count.idcorrevent] = count.masked - 1
        return res

    def get_data(self, event):
        return {
            'id': event[0].idcorrevent,
        }

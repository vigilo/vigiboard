# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2016 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Module complémentaire générique.
"""

# État lorsque les plugins sont appelés avec les sous-requêtes.
INNER = 0
# État lorsque les plugins sont appelés lorsque "items" est défini.
ITEMS = 1


class VigiboardRequestPlugin(object):
    """
    Classe que les plugins de VigiBoard doivent étendre.
    """

    def get_bulk_data(self, events_ids):
        """
        Cette méthode est appelée par le L{RootController} : elle
        retourne toutes les données affichées par le plugin dans le
        tableau des évènements de la page principale de VigiBoard.

        Cette méthode DEVRAIT être surchargée dans les classes dérivées.

        @param events_ids: Liste des identifiants des C{CorrEvent} affichés
            sur la page.
        @type  events_ids:  C{List} of C{int}
        @return: Dictionnaire associant à chaque identifiant
            d'évènement les données à afficher par le plugin.
        @rtype:  C{dict}
        """
        pass

    def get_json_data(self, idcorrevent, *args, **kwargs):
        """
        Cette méthode est appelée par le template du plugin via
        la méthode get_plugin_json_data du L{RootController} de VigiBoard.

        Cette méthode DEVRAIT être surchargée dans les classes dérivées
        si le plugin en question doit avoir recours à une requête JSON.

        @param idcorrevent: Identifiant du C{CorrEvent} à interroger.
        @type idcorrevent:  C{int}
        @return: Dictionnaire contenant la ou les valeur(s) correspondantes.
        @rtype:  C{dict}
        """
        pass

    def get_generated_columns_count(self):
        """
        Cette méthode renvoie le nombre de colonnes ajoutées dans le tableau
        des événements par ce plugin. Par défaut, on suppose que chaque plugin
        n'ajoute qu'une seule colonne au tableau.

        Cette méthode PEUT être surchargée dans les classes dérivées.

        @return: Nombre de colonnes ajoutées par ce plugin.
        @rtype: C{int}
        """
        return 1

    def get_data(self, event):
        return {}

    def get_search_fields(self):
        return []

    def get_sort_criterion(self, query, column):
        """
        Cette méthode renvoie le critère à utiliser par SQLAlchemy pour trier
        la requête alimentant le tableau des événements.

        Cette méthode DEVRAIT être surchargée dans les classes dérivées
        si le plugin en question implémente un tri.

        @param query: La requête VigiBoard servant à alimenter le tableau des
            événements.
        @type  query: L{VigiboardRequest}
        @param column: La colonne sur laquelle l'utilisateur souhaite opérer le
            tri.
        @type column: C{str}
        """
        pass

    def handle_search_fields(self, query, search, state, subqueries):
        pass

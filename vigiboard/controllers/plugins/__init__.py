# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
################################################################################
#
# Copyright (C) 2007-2011 CS-SI
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
Module complémentaire générique.
"""

from pylons.i18n import ugettext as _

class VigiboardRequestPlugin(object):
    """
    Classe que les plugins de VigiBoard doivent étendre.
    """

    def __init__ (self, table = None, join = None, outerjoin = None,
            filters = None, groupby = None, orderby = None, name = '',
            style = None, object_name = ""):
        self.table = table
        self.join = join
        self.outerjoin = outerjoin
        self.filter = filters
        self.orderby = orderby
        self.name = name
        self.groupby = groupby
        self.style = style
        self.object_name = object_name

    def get_bulk_data(self, events_ids):
        """
        Cette méthode est appelée par le L{RootController} : elle
        retourne toutes les données affichées par le plugin dans le
        tableau des évènements de la page principale de VigiBoard.

        Cette méthode DEVRAIT être surchargée dans les classes dérivées.

        @param event_ids: Liste des identifiants des C{CorrEvent} affichés
            sur la page.
        @type events_id:  C{List} of C{int}
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

    def get_search_fields(self):
        return []

    def handle_search_fields(self, query, search):
        pass

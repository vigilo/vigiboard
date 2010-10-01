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
Un plugin pour VigiBoard qui ajoute 3 colonnes au tableau des événements :
    -   la première colonne contient l'état d'acquittement de l'événement.
    -   la seconde colonne contient un lien permettant d'éditer certaines
        propriétés associées à l'événement corrélé.
    -   la dernière colonne permet de (dé)sélectionner l'événement pour
        effectuer un traitement par lot.
"""
from vigiboard.controllers.plugins import VigiboardRequestPlugin

class PluginStatus(VigiboardRequestPlugin):
    """
    Ajoute des colonnes permettant de voir le statut d'acquittement
    d'un événement corrélé et de modifier certaines de ses propriétés.
    """

    def get_generated_columns_count(self):
        """
        Renvoie le nombre de colonnes que ce plugin ajoute.
        Ce plugin en ajoute 4, au lieu de 1 comme la plupart des plugins.
        """
        return 4

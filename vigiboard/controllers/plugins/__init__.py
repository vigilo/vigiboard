# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
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

    def get_value(self, idcorrevent, *args, **kwargs):
        """
        Cette méthode est appelée lorsque l'on demande la valeur du plugin
        grâce à la méthode get_plugin_value du L{RootController} de VigiBoard.

        Cette méthode DEVRAIT être surchargée dans les classes dérivées.

        @param idcorrevent: Identifiant du L{CorrEvent} à interroger.
        @type idcorrevent: C{int}
        @return: Dictionnaire contenant la ou les valeur(s) correspondantes.
        @rtype: C{dict}
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


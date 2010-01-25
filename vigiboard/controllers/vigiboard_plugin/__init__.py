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

    def __show__ (self, aggregate):
        """
        Permet d'éviter toutes erreurs d'affichage.
        C'est la fonction appelée par le formateur d'événements.
        """

        show = self.show(aggregate)

        if show != None:
            try:
                return str(show)
            except:
                return _('Error')

    def show(self, aggregate):
        """
        Fonction qui affichera par défaut une chaîne de
        caractères vide dans la colonne attribuée au plugin.

        En général, les plugins devront redéfinir cette fonction
        pour afficher ce qu'ils souhaitent.
        """

        return ''

    def context(self, context):
        """
        Fonction permettant d'ajouter un contexte dans la page d'événements,
        comme par exemple un fichier CSS ou une fonction Javascript.
        """

        pass
 
    
    def controller(self):
        """
        Fonction permettant de rajouter un pseudo-contrôleur pour le plugin.
        Ceci permet par exemple d'exécuter des requêtes JSON.
        """

        pass

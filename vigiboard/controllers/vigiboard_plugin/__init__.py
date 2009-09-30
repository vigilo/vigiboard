# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""
Generic plugin
"""

from pylons.i18n import ugettext as _

class VigiboardRequestPlugin(object):

    """
    Classe dont les plugins utilisé dans VigiboardRequest doivent étendre.
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
        C'est la fonction appelée par le formateur d'évènements.
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
        Fonction permettant de rajouter du context à la page d'évènements,
        comme par exemple un css ou une fonction Javascript
        """

        pass
 
    
    def controller(self):

        """
        Fonction permettant de rajouter un pseudo controller pour le plugin.
        Ceci permet par exemple de faire de appels json
        """

        pass

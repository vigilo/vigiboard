# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 

class VigiboardRequestPlugin(object):

    """
    Classe dont les plugins utilisé dans VigiboardRequest doivent étendre.
    """

    def __init__ (self, table = None, join = None, outerjoin = None,
            filters = None, groupby = None, orderby = None, name = '',
            style = None):

        self.table = table
        self.join = join
        self.outerjoin = outerjoin
        self.filter = filters
        self.orderby = orderby
        self.name = name
        self.groupby = groupby
        self.style = style

    def __show__ (self, event):

        """
        Permet d'éviter toutes erreurs d'affichage.
        C'est la fonction appelé par le formateur d'évènements.
        """

        show = self.show(event)

        if show != None :
            try:
                return str(show)
            except:
                return _('Error')

    def show(self, event):

        """
        Fonction qui affichera par défaut une chaîne de
        caractères vide dans la colonne attribué au plugin.

        En général, les plugins devront redéfinir cette fonction
        pour afficher ce qu'ils souhaitent.
        """

        return ''


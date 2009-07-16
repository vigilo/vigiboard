# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Fonctions utiles en rapport avec l'utilisateur"""

from vigiboard.model import DBSession, Permission, Groups, GroupPermissions
from sets import Set
import tg 

def get_user_groups():
    
    """
    Permet de connaître l'ensemble des groups d'hôte et de service de vigiboard
    auquel l'utilisateur appartient

    @return: Liste des groups
    """

    # Requête permettant d'obtenir les groups directs de l'utilisateur

    groups = DBSession.query(Groups.name).join(
        ( GroupPermissions , Groups.name == GroupPermissions.groupname ),
        ( Permission ,
            Permission.permission_id == GroupPermissions.idpermission )
        ).filter(Permission.permission_name.in_(
            tg.request.environ.get('repoze.who.identity').get('permissions')
        ))
    
    lst_grp = Set([i.name for i in groups])
    lst_tmp = lst_grp
    
    # On recherche maintenant les groupes indirect
    
    while len(lst_tmp) > 0:
        groups = DBSession.query(Groups.name).filter(Groups.parent.in_(lst_tmp))
        tmp = Set([])
        for i in groups :
            tmp.add(i.name)
            lst_grp.add(i.name)
        lst_tmp = tmp

    return lst_grp

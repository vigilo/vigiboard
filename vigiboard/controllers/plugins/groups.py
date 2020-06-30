# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2020 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Un plugin pour VigiBoard qui ajoute une colonne avec les groupes
d'éléments supervisés auxquels appartient l'objet associé
à l'événement corrélé.
"""
import tw.forms as twf
from tg.i18n import lazy_ugettext as l_

from vigiboard.controllers.plugins import VigiboardRequestPlugin, INNER
from vigilo.models.session import DBSession
from vigilo.models import tables
from vigilo.models.tables.group import Group
from vigilo.models.tables.grouphierarchy import GroupHierarchy
from vigilo.models.tables.secondary_tables import SUPITEM_GROUP_TABLE
from sqlalchemy.orm import aliased
from sqlalchemy import or_


class GroupSelector(twf.InputField):
    params = ["choose_text", "text_value", "clear_text"]
    choose_text = l_('Choose')
    clear_text = l_('Clear')
    text_value = ''

    template = """
<div xmlns="http://www.w3.org/1999/xhtml"
   xmlns:py="http://genshi.edgewall.org/" py:strip="">
<input type="hidden" name="${name}" class="${css_class}"
    id="${id}.value" value="${value}" py:attrs="attrs" />
<input type="text" class="${css_class}" id="${id}.ui"
    value="${text_value}" readonly="readonly" py:attrs="attrs" />
<input type="button" class="${css_class}" id="${id}"
    value="${choose_text}" py:attrs="attrs" />
<input type="button" class="${css_class}" id="${id}.clear"
    value="${clear_text}" py:attrs="attrs" />
</div>
"""

    def update_params(self, d):
        super(GroupSelector, self).update_params(d)
        text_value = DBSession.query(Group.name).filter(
                        Group.idgroup == d.value).scalar()
        if not text_value:
            d.value = ''
        else:
            d.text_value = text_value


class PluginGroups(VigiboardRequestPlugin):
    """
    Affiche les groupes d'éléments supervisés auxquels
    appartient l'événement corrélé.
    """
    def get_search_fields(self):
        return [
            GroupSelector(
                'supitemgroup',
                label_text=l_('Group'),
                validator=twf.validators.Int(if_invalid=None, if_missing=None),
            )
        ]

    def handle_search_fields(self, query, search, state, subqueries):
        if search.get('supitemgroup') is None or state != INNER:
            return

        # Il s'agit d'un manager. On applique le filtre
        # indépendamment aux 2 sous-requêtes.
        if len(subqueries) == 2:
            subqueries[0] = subqueries[0].join(
                (SUPITEM_GROUP_TABLE,
                    or_(
                        SUPITEM_GROUP_TABLE.c.idsupitem == \
                            tables.LowLevelService.idhost,
                        SUPITEM_GROUP_TABLE.c.idsupitem == \
                            tables.LowLevelService.idservice,
                    )
                ),
                (GroupHierarchy, GroupHierarchy.idchild ==
                    SUPITEM_GROUP_TABLE.c.idgroup)
            ).filter(
                GroupHierarchy.idparent == search['supitemgroup']
            )

            subqueries[1] = subqueries[1].join(
                (SUPITEM_GROUP_TABLE,
                    SUPITEM_GROUP_TABLE.c.idsupitem == \
                        tables.Host.idhost,
                ),
                (GroupHierarchy, GroupHierarchy.idchild ==
                    SUPITEM_GROUP_TABLE.c.idgroup)
            ).filter(
                GroupHierarchy.idparent == search['supitemgroup']
            )

        # Il s'agit d'un utilisateur normal.
        else:
            GroupHierarchy_aliased = aliased(GroupHierarchy,
                name='GroupHierarchy_aliased')
            subqueries[0] = subqueries[0].join(
                (GroupHierarchy_aliased, GroupHierarchy_aliased.idchild ==
                    tables.UserSupItem.idsupitemgroup)
            ).filter(
                 GroupHierarchy_aliased.idparent == search['supitemgroup']
            )


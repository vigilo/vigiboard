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
Un plugin pour VigiBoard qui ajoute une colonne avec les groupes
d'éléments supervisés auxquels appartient l'objet associé
à l'événement corrélé.
"""
import tw.forms as twf
from pylons.i18n import lazy_ugettext as l_

from vigiboard.controllers.plugins import VigiboardRequestPlugin
from vigilo.models.session import DBSession
from vigilo.models.tables.group import Group
from vigilo.models.tables.grouphierarchy import GroupHierarchy

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

    def handle_search_fields(self, query, search):
        if search.get('supitemgroup'):
            query.add_join((GroupHierarchy, GroupHierarchy.idchild ==
                query.items.c.idsupitemgroup))
            query.add_filter(GroupHierarchy.idparent ==
                search['supitemgroup'])

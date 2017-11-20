# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Un plugin pour VigiBoard qui ajoute une colonne avec la priorité
ITIL de l'événement corrélé.
"""
import tw2.forms as twf
from formencode import validators
from tg.i18n import lazy_ugettext as l_

from vigilo.models.tables import CorrEvent, StateName
from vigiboard.controllers.plugins import VigiboardRequestPlugin, ITEMS

from tw2.forms.widgets import BaseLayout, FormField

class HorizontalBox(BaseLayout, FormField):
    """
    Container de widgets, qui se contente de les placer
    côte-à-côte horizontalement.
    """
    inline_engine_name = "genshi"
    template = """<div xmlns:py="http://genshi.edgewall.org/"
        id="${w.compound_id}" name="${w.name}">
    <py:for each="c in w.children_non_hidden">
        ${c.display()}
    </py:for>
</div>
"""

    def generate_schema(self):
        """
        Fait en sorte que l'absence de saisie dans les sous-champs
        du container ne génère pas une erreur (Valeur manquante)
        sur le container lui-même.
        """
        super(HorizontalBox, self).generate_schema()
        self.validator.if_missing = None


class PluginPriority(VigiboardRequestPlugin):
    """
    Ce plugin affiche la priorité ITIL des événements corrélés.
    La priorité est un nombre entier et permet de classer les événements
    corrélés dans l'ordre qui semble le plus approprié pour que les
    problèmes les plus urgents soient traités en premier.

    La priorité des événements peut être croissante (plus le nombre est
    élevé, plus il est urgent de traiter le problème) ou décroissante
    (ordre opposé). L'ordre utilisé par VigiBoard pour le tri est
    défini dans la variable de configuration C{vigiboard_priority_order}.
    """

    def get_search_fields(self):
        options = [
            ('eq',  u'='),
            ('neq', u'≠'),
            ('gt',  u'>'),
            ('gte', u'≥'),
            ('lt',  u'<'),
            ('lte', u'≤'),
        ]

        return [
            HorizontalBox(
                'priority',
                label=l_('Priority'),
                children=[
                    twf.SingleSelectField(
                        'op',
                        options=options,
                        validator=validators.OneOf(
                            dict(options).keys(),
                            if_invalid=None,
                            if_missing=None,
                        ),
                    ),
                    twf.TextField(
                        'value',
                        validator=validators.Int(
                            if_invalid=None,
                            if_missing=None,
                        ),
                    ),
                ],
            )
        ]

    def handle_search_fields(self, query, search, state, subqueries):
        if (not search.get('priority')) or state != ITEMS:
            return

        op = search['priority']['op']
        value = search['priority']['value']

        if (not op) or (not value):
            search['priority'] = None
            return

        if op == 'eq':
            query.add_filter(CorrEvent.priority == value)
        elif op == 'neq':
            query.add_filter(CorrEvent.priority != value)
        elif op == 'gt':
            query.add_filter(CorrEvent.priority > value)
        elif op == 'gte':
            query.add_filter(CorrEvent.priority >= value)
        elif op == 'lt':
            query.add_filter(CorrEvent.priority < value)
        elif op == 'lte':
            query.add_filter(CorrEvent.priority <= value)

    def get_data(self, event):
        state = StateName.value_to_statename(event[0].cause.current_state)
        return {
            'state': state,
            'priority': event[0].priority,
        }

    def get_sort_criterion(self, query, column):
        if column == 'priority':
            return CorrEvent.priority
        return None


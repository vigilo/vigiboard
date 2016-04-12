# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2016 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Un plugin pour VigiBoard qui ajoute 3 colonnes au tableau des événements :
    -   la première colonne contient l'état d'acquittement de l'événement.
    -   la seconde colonne contient un lien permettant d'éditer certaines
        propriétés associées à l'événement corrélé.
    -   la dernière colonne permet de (dé)sélectionner l'événement pour
        effectuer un traitement par lot.
"""
import urllib
import tg
import tw.forms as twf
from pylons.i18n import lazy_ugettext as l_

from vigilo.models.tables import CorrEvent, StateName
from vigilo.models.functions import sql_escape_like
from vigiboard.controllers.plugins import VigiboardRequestPlugin, ITEMS

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

    def get_search_fields(self):
        options = [
            ('', l_('All alerts')),
            # On doit passer un type basestring pour les options.
            # Donc, on convertit les constantes (entiers) en type str.
            (str(CorrEvent.ACK_NONE),   l_('New alerts')),
            (str(CorrEvent.ACK_KNOWN),  l_('Alerts marked as Acknowledged')),
            (str(CorrEvent.ACK_CLOSED), l_('Alerts marked as Closed')),
        ]

        return [
            twf.TextField(
                'trouble_ticket',
                label_text=l_('Trouble Ticket'),
                validator=twf.validators.String(if_missing=None),
            ),
            twf.SingleSelectField(
                'ack',
                label_text=l_('Acknowledgement Status'),
                options=options,
                validator=twf.validators.OneOf(
                    dict(options).keys(),
                    if_invalid=None,
                    if_missing=None,
                ),
            ),
        ]

    def handle_search_fields(self, query, search, state, subqueries):
        if state != ITEMS:
            return

        if search.get('trouble_ticket'):
            tt = sql_escape_like(search['trouble_ticket'])
            query.add_filter(CorrEvent.trouble_ticket.ilike(tt))

        if search.get('ack'):
            try:
                query.add_filter(CorrEvent.ack == int(search['ack']))
            except (ValueError, TypeError):
                # On ignore silencieusement le critère de recherche erroné.
                pass

    def get_data(self, event):
        cause = event[0].cause
        ack = event[0].ack
        state = StateName.value_to_statename(cause.current_state)

        trouble_ticket_id = None
        trouble_ticket_link = None
        if event[0].trouble_ticket:
            trouble_ticket_id = event[0].trouble_ticket
            trouble_ticket_link = tg.config['vigiboard_links.tt'] % {
                'id': event[0].idcorrevent,
                'host': event[1] and urllib.quote(event[1].encode('utf8'), '') or event[1],
                'service': event[2] and urllib.quote(event[2].encode('utf8'), '') or event[2],
                'tt': trouble_ticket_id and \
                        urllib.quote(trouble_ticket_id.encode('utf8'), '') or \
                        trouble_ticket_id,
            }

        return {
            'trouble_ticket_link': trouble_ticket_link,
            'trouble_ticket_id': trouble_ticket_id,
            'state': state,
            'id': event[0].idcorrevent,
            'ack': ack,
        }

    def get_sort_criterion(self, query, column):
        criteria = {
            'ticket': CorrEvent.trouble_ticket,
            'ack': CorrEvent.ack,
        }
        return criteria.get(column)


# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Un plugin pour VigiBoard qui ajoute une colonne avec les liens vers les
entrées d'historiques liées à l'événement, ainsi que les liens vers les
applications externes.
"""

import urllib

from tg.exceptions import HTTPNotFound
from tg import flash, request, config, redirect, url
from pylons.i18n import ugettext as _

from vigiboard.controllers.vigiboardrequest import VigiboardRequest
from vigiboard.controllers.vigiboard_plugin import VigiboardRequestPlugin
from vigilo.models.configure import DBSession
from vigilo.models import User, CorrEvent, Event, StateName

class PluginHistory(VigiboardRequestPlugin):
    """
    Plugin qui ajoute des liens vers les historiques et les applications
    externes.
    """

    def get_value(self, idcorrevent, *args, **kwargs):
        """
        Renvoie les éléments pour l'affichage de la fenêtre de dialogue
        contenant des liens internes et externes.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param id: identifiant de l'événement
        """

        # Obtention de données sur l'événement et sur son historique
        username = request.environ.get('repoze.who.identity'
                    ).get('repoze.who.userid')

        username = request.environ['repoze.who.identity']['repoze.who.userid']
        events = VigiboardRequest(User.by_user_name(username))
        events.add_table(
            Event,
            events.items.c.hostname,
            events.items.c.servicename,
        )
        events.add_join((CorrEvent, CorrEvent.idcause == Event.idevent))
        events.add_join((events.items, 
            Event.idsupitem == events.items.c.idsupitem))
        events.add_filter(CorrEvent.idcorrevent == idcorrevent)

        # Vérification que au moins un des identifiants existe et est éditable
        # TODO: on est dans du JSON, donc flash/redirect ne fonctionneront pas!
        if events.num_rows() != 1:
            flash(_('No access to this event'), 'error')
            redirect('/')

        event = events.req[0]
        eventdetails = {}
        for edname, edlink in \
                config['vigiboard_links.eventdetails'].iteritems():

            # Rappel:
            # event[0] = priorité de l'alerte corrélée.
            # event[1] = alerte brute.
            if event.servicename:
                service = urllib.quote(event.servicename)
            else:
                service = None
            eventdetails[edname] = edlink[1] % {
                'idcorrevent': idcorrevent,
                'host': urllib.quote(event.hostname),
                'service': service,
                'message': urllib.quote(event[0].message),
            }

        return dict(
                current_state = StateName.value_to_statename(
                                    event[0].current_state),
                initial_state = StateName.value_to_statename(
                                    event[0].initial_state),
                peak_state = StateName.value_to_statename(
                                    event[0].peak_state),
                idcorrevent = idcorrevent,
                host = event.hostname,
                service = event.servicename,
                eventdetails = eventdetails,
            )



# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""Gestion de la requête, des plugins et de l'affichage du Vigiboard"""

from time import mktime
from logging import getLogger

from tg import url, config, tmpl_context
from tg.i18n import get_lang
from pylons.i18n import ugettext as _
from sqlalchemy import not_, and_, asc, desc, sql
from sqlalchemy.sql.expression import or_, null as expr_null, union
from sqlalchemy.orm import aliased

from vigilo.models.session import DBSession
from vigilo.models import SupItem, Event, CorrEvent, EventHistory, \
                        Host, HostGroup, LowLevelService, ServiceGroup, \
                        StateName
from vigilo.models.secondary_tables import HOST_GROUP_TABLE, \
                                            SERVICE_GROUP_TABLE
from vigiboard.widgets.edit_event import EditEventForm
from vigiboard.widgets.search_form import SearchForm
from vigiboard.controllers.vigiboard_plugin import VigiboardRequestPlugin
from vigilo.common.conf import settings

LOGGER = getLogger(__name__)

class VigiboardRequest():
    """
    Classe gérant la génération de la requête finale,
    le préformatage des événements et celui des historiques
    """

    class_ack = {
        'None': '',
        'Acknowledged': '_Ack',
        'AAClosed': '_Ack',
    }

    def __init__(self, user):
        """
        Initialisation de toutes les variables nécessaires :
        - la liste des groupes de l'utilisateur,
        - la langue de l'utilisateur
        - les différentes étapes de la génération de la requête,
        - la liste des plugins à appliquer.
        """

        # TODO: Utiliser le champ "language" du modèle pour cet utilisateur ?
        # On récupère la langue du navigateur de l'utilisateur
        lang = get_lang()
        if not lang:
            lang = settings['VIGILO_ALL_DEFAULT_LANGUAGE']
        else:
            lang = lang[0]

        self.user_groups = user.groups
        self.lang = lang
        self.generaterq = False
        
        lls_query = DBSession.query(
            LowLevelService.idservice.label("idsupitem"),
            LowLevelService.servicename.label("servicename"),
            Host.name.label("hostname"),
            SERVICE_GROUP_TABLE.c.idgroup.label("idservicegroup"),
            HOST_GROUP_TABLE.c.idgroup.label("idhostgroup"),
        ).join(
           (Host, Host.idhost == LowLevelService.idhost),
        ).outerjoin(
            (HOST_GROUP_TABLE, HOST_GROUP_TABLE.c.idhost == LowLevelService.idhost),
            (SERVICE_GROUP_TABLE, SERVICE_GROUP_TABLE.c.idservice == LowLevelService.idservice),
        ).filter(
            or_(
                HOST_GROUP_TABLE.c.idgroup.in_(self.user_groups),
                SERVICE_GROUP_TABLE.c.idgroup.in_(self.user_groups),
            ),
        )
               
        host_query = DBSession.query(
            Host.idhost.label("idsupitem"),
            expr_null().label("servicename"),
            Host.name.label("hostname"),
            expr_null().label("idservicegroup"),
            HOST_GROUP_TABLE.c.idgroup.label('idhostgroup'),
        ).join((HOST_GROUP_TABLE, HOST_GROUP_TABLE.c.idhost == Host.idhost)
        ).filter(HOST_GROUP_TABLE.c.idgroup.label('idhostgroup').in_(self.user_groups),
        )

        # Object Selectable renvoyant des informations sur un supitem
        # concerné par une alerte, avec prise en compte des droits d'accès.
        # On est obligés d'utiliser sqlalchemy.sql.expression.union
        # pour indiquer à SQLAlchemy de NE PAS regrouper les tables
        # dans la requête principale, sans quoi les résultats sont
        # incorrects.
        self.items = union(lls_query, host_query, correlate=False).alias()

        # Éléments à retourner (SELECT ...)
        self.table = []

        # Tables sur lesquelles porte la récupération (JOIN)
        self.join = []

        # Tables sur lesquelles porte la récupération (OUTER JOIN)
        self.outerjoin = []

        # Critères de filtrage (WHERE)
        self.filter = [
            # On masque les événements avec l'état OK
            # et traités (status == u'AAClosed').
            not_(and_(
                StateName.statename.in_([u'OK', u'UP']),
                CorrEvent.status == u'AAClosed'
            )),
            CorrEvent.timestamp_active != None,
        ]

        # Permet de définir le sens de tri pour la priorité.
        if config['vigiboard_priority_order'] == 'asc':
            priority_order = asc(CorrEvent.priority)
        else:
            priority_order = desc(CorrEvent.priority)

        # Tris (ORDER BY)
        self.orderby = [
            desc(CorrEvent.status),         # None, Acknowledged, AAClosed
            priority_order,                 # Priorité ITIL (entier).
            desc(StateName.order),          # Etat courant (entier).
            desc(Event.timestamp),
            asc(self.items.c.hostname),
        ]

        # Regroupements (GROUP BY)
        self.groupby = [
            StateName.order,
            Event.timestamp,
            CorrEvent.status,
            CorrEvent.priority,
        ]

        self.plugin = []
        self.events = []
        self.idevents = []
        self.hist = []
        self.req = DBSession
        self.context_fct = []

    def add_plugin(self, *argv):
        """
        Ajout d'un plugin, on lui prélève ses ajouts dans la requête
        """
        for i in argv:
            if isinstance(i, VigiboardRequestPlugin):
                if i.table:
                    self.add_table(*i.table)
                if i.join:
                    self.add_join(*i.join)
                if i.outerjoin:
                    self.add_outer_join(*i.outerjoin)
                if i.filter:
                    self.add_filter(*i.filter)
                if i.groupby:    
                    self.add_group_by(*i.groupby)
                if i.orderby:
                    self.add_order_by(*i.orderby)
                self.plugin.append(i)

    def generate_request(self):
        """
        Génération de la requête avec l'ensemble des données stockées
        et la place dans la variable rq de la classe
        """
        if self.generaterq:
            return

        for plug in config.get('vigiboard_plugins', []):
            try:
                mypac = __import__(
                    'vigiboard.controllers.vigiboard_plugin.' +\
                            plug[0], globals(), locals(), [plug[1]], -1)
                self.add_plugin(getattr(mypac, plug[1])())
            except ImportError:
                # On loggue l'erreur et on ignore le plugin.
                LOGGER.error(_('No such plugin "%s"') % plug[0])

        self.join.extend([
            (self.items, Event.idsupitem == self.items.c.idsupitem),
            (StateName, StateName.idstatename == Event.current_state),
        ])
        self.add_group_by(*self.table)

        # query et join ont besoin de referrence
        self.req = self.req.query(*self.table)
        self.req = self.req.join(*self.join)

        # le reste, non
        for i in self.outerjoin:
            self.req = self.req.outerjoin(i)
        for i in self.filter:
            self.req = self.req.filter(i)
        for i in self.groupby:
            self.req = self.req.group_by(i)
        for i in self.orderby:
            self.req = self.req.order_by(i)

        self.generaterq = True

    def num_rows(self):
        """
        Retourne le nombre de lignes de la requête.
        Si celle-ci n'est pas encore générée, on le fait.

        @return: Nombre de ligne
        """

        self.generate_request()
        return self.req.count()

    def add_table(self, *argv):
        """
        Ajoute une ou plusieurs tables/élément d'une table à
        la requête.

        @param argv: Liste des tables à ajouter
        """
        
        # On vérifie qu'il n'y a pas de doublons dans la liste finale
        # des tables.
        
        for i in argv :
            for j in self.table:
                if str(i) == str(j):
                    break
            self.table.append(i)

    def add_join(self, *argv):
        """
        Ajoute une ou plusieurs jointures à
        la requête.

        @param argv: Liste des jointures à ajouter
        """
        
        # On vérifie qu'il n'y a pas de doublons dans la liste finale
        # des jointures.
        
        for i in argv:
            for j in self.join:
                if str(i) == str(j):
                    break
            self.join.append(i)

    def add_outer_join(self, *argv):
        """
        Ajoute une ou plusieurs jointures externes à
        la requête.

        @param argv: Liste des jointures externes à ajouter
        """
        
        # On vérifie qu'il n'y a pas de doublons dans la liste finale
        # des jointures externes.
        
        for i in argv:
            for j in self.outerjoin:
                if str(i) == str(j):
                    break
            self.outerjoin.append(i)    

    def add_filter(self, *argv):
        """
        Ajoute un ou plusieurs filtres à la requête.

        @param argv: Liste des filtres à ajouter
        """
        
        # On vérifie qu'il n'y a pas de doublons dans la liste finale
        # des filtres.
        
        for i in argv:
            for j in self.filter:
                if str(i) == str(j):
                    break
            self.filter.append(i)

    def add_group_by(self, *argv):
        """
        Ajoute un ou plusieurs groupements à la requête.

        @param argv: Liste des groupements à ajouter
        """
        
        # On vérifie qu'il n'y a pas de doublons dans la liste finale
        # des groupements.
        
        for i in argv:
            for j in self.groupby:
                try:
                    if str(i) == str(j):
                        break
                # SQLAlchemy lève cette exception pour certains attributes,
                # par exemple les attributs définis avec synonym().
                except AttributeError:
                    pass
            self.groupby.append(i)

    def add_order_by(self, *argv):
        """
        Ajoute un ou plusieurs orders à la requête.

        @param argv: Liste des ordres à ajouter
        """
        
        # On vérifie qu'il n'y a pas de doublons dans la liste finale
        # des ordres.
        
        for i in argv:
            for j in self.orderby:
                if str(i) == str(j):
                    break
            self.orderby.append(i)

    def format_events_status(self, event):
        """
        Suivant l'état de l'événement, retourne la classe à appliquer
        à l'image indiquant si l'événement est pris en compte ou non,
        ainsi qu'un texte indiquant l'état.

        @param event: l'événement à analyser

        @return: Dictionnaire représentant la classe à appliquer
            et l'état (sous une forme intelligible).
        """

        if event.status == 'AAClosed':
            return {
                'src': url('/images/crossed.png'),
                'label': _('Closed'),
            }
        elif event.status == 'Acknowledged':
            return {
                'src': url('/images/checked.png'),
                'label': _('Acknowledged'),
            }
        else:
            return None

    def format_events(self, first_row, last_row):
        """
        Formate la réponse de la requête et y applique les plugins
        pour un affichage simple du résultat par Genshi.
        On génère une liste de liste, chaqu'une étant la description de
        l'affichage pour un événement donné.

        @param first_row: Indice de début de la liste des événements
        @param last_row: Indice de fin de la liste des événements
        """
        
        # Si la requête n'est pas générée, on le fait
        self.generate_request()

        # Liste des éléments pour la tête du tableau

        lst_title = [
                ['',{}],
                [_('Date')+ '<span style="font-weight:normal">' + \
                        '<br />['+_('Duration') + ']</span>',
                        {'style':'text-align:left'}],
                [_('Priority'), {'title':_('ITIL Priority')}],
                ['#', {'title':_('Occurrence count')}],
                [_('Host'), {'style':'text-align:left'}],
                [_('Service Type')+'<br />'+_('Service Name'),
                    {'style':'text-align:left'}], 
                [_('Output'), {'style':'text-align:left'}]
                ]
        lst_title.extend([[plug.name, plug.style] for plug in self.plugin])
        lst_title.extend([['[' + _('TT') + ']', {'title': _('Trouble Ticket')}],
                            ['', {}]])
        events = [lst_title]
        i = 0
        class_tr = ['odd', 'even']
        ids = []
        for req in self.req[first_row : last_row]:
            # Si il y a plus d'un élément dans la liste des tables,
            # req devient une liste plutôt que d'être directement la
            # table souhaitée

            if isinstance(req, CorrEvent):
                event = req
            else:
                event = req[0]
                hostname = req.hostname
                servicename = req.servicename
            ids.append(event.idcause)

            # La liste pour l'événement actuel comporte dans l'ordre :
            #   L'événement en lui-même
            #   La classe à appliquer sur la ligne (permet d'alterner les
            #       couleurs suivant les lignes)
            #   La classe pour la case comportant la flèche de détails
            #   La classe pour la date, l'occurence et l'édition
            #   L'image à afficher pour la flèche de détails
            #   Une liste (une case par plugin) de ce que le plugin souhaite
            #       afficher en fonction de l'événement

            cause = event.cause

            events.append([
                    event,
                    hostname,
                    servicename,
                    {'class': class_tr[i % 2]},
                    {'class': StateName.value_to_statename(
                        cause.initial_state) +
                        self.class_ack[event.status]},
                    {'class': StateName.value_to_statename(
                        cause.current_state) +
                        self.class_ack[event.status]},
                    {'src': '/images/%s2.png' %
                        StateName.value_to_statename(
                        cause.current_state)},
                    self.format_events_status(event),
                    [[j.__show__(event), j.style] for j in self.plugin]
                ])
            i += 1

        # On sauvegarde la liste précédemment créée puis on remplit
        # le TmplContext
        self.events = events
        self.idevents = ids

    def format_history(self):
        """
        Formate les historiques correspondant aux événements sélectionnés
        pour un affichage simple du résultat par Genshi.
        On génère une liste de liste, chaqu'une étant la description
        de l'affichage pour un historique donné.
        """

        history = DBSession.query(
                    EventHistory,
                ).filter(EventHistory.idevent.in_(self.idevents)
                ).order_by(desc(EventHistory.timestamp)
                ).order_by(desc(EventHistory.idhistory))
        if history.count() == 0:
            self.hist = {}
            for i in self.idevents:
                self.hist[i] = []
            return

        hists = {}
        i = 0
        class_tr = ['odd', 'even']

        for hist in history:
            if not hist.idevent in hists:
                hists[hist.idevent] = []

            # La liste pour l'historique actuel comporte dans l'ordre :
            #   Le moment où il a été généré
            #   Qui l'a généré
            #   Le type d'action qui a été appliqué
            #   La valeur de l'action
            #   Le détail de l'action
            #   La classe à appliquer à la ligne
            #       (permet d'alterner les couleurs)

            hists[hist.idevent].append([
                hist.timestamp,
                hist.username,
                hist.type_action,
                hist.value,
                hist.text,
                {'class': class_tr[i % 2]},
            ])
            i += 1
        
        self.hist = hists

    def generate_tmpl_context(self):
        """
        Génère et peuple la variable tmpl_context avec les Dialogs et
        formulaires nécessaire au fonctionnement de Vigiboard
        """

        from vigiboard.controllers.root import get_last_modification_timestamp
        
        # Dialogue d'édition
        tmpl_context.edit_event_form = EditEventForm('edit_event_form',
            last_modification=mktime(get_last_modification_timestamp(
                self.idevents).timetuple()),
            action=url('/update'), 
        )

        # Dialogue de recherche
        tmpl_context.search_form = SearchForm('search_form', lang=self.lang,
                                        # TRANSLATORS: Format de date et heure.
                                        date_format=_('%Y-%m-%d %I:%M:%S %p'))
        
        # Dialogue de détail d'un événement

        # Exécution des contexts des plugins
        for j in self.plugin:
            j.context(self.context_fct)


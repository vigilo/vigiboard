# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2019 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Gestion de la requête, des plugins et de l'affichage du Vigiboard"""

import logging
from time import mktime

from tg import config, tmpl_context, request, url
from tg.i18n import ugettext as _
from paste.deploy.converters import aslist

from sqlalchemy import not_, and_, asc, desc
from sqlalchemy.sql.expression import null as expr_null, union_all
from sqlalchemy.orm import contains_eager

from vigilo.models.session import DBSession
from vigilo.models.tables import Event, CorrEvent, EventHistory, \
    Host, LowLevelService, StateName, UserSupItem
from vigiboard.widgets.edit_event import EditEventForm
from vigiboard.controllers.plugins import VigiboardRequestPlugin, INNER, ITEMS

LOGGER = logging.getLogger(__name__)

class VigiboardRequest():
    """
    Classe gérant la génération de la requête finale,
    le préformatage des événements et celui des historiques
    """

    def __init__(self, user, mask_closed_events=True, search=None, sort=None, order=None):
        """
        Initialisation de l'objet qui effectue les requêtes de VigiBoard
        sur la base de données.
        Cet objet est responsable de la vérification des droits de
        l'utilisateur sur les données manipulées.

        @param user: Nom de l'utilisateur cherchant à afficher les événements.
        @type  user: C{str}
        @param mask_closed_events: Booléen indiquant si l'on souhaite masquer les
            événements fermés ou non.
        @type  mask_closed_events: C{boolean}
        @param search: Dictionnaire contenant les critères de recherche.
        @type  search: C{dict}
        @param sort: Colonne de tri; vide en l'absence de tri.
        @type  sort: C{unicode}
        @param order: Ordre du tri ("asc" ou "desc"); vide en l'absence de tri.
        @type  order: C{unicode}

        """

        # Permet s'appliquer des filtres de recherche aux sous-requêtes.
        self.subqueries = []
        self.generaterq = False

        # Éléments à retourner (SELECT ...)
        self.table = []

        # Tables sur lesquelles porte la récupération (JOIN)
        self.join = []

        # Options à ajouter la requête
        self.option = []

        # Tables sur lesquelles porte la récupération (OUTER JOIN)
        self.outerjoin = []

        # Critères de filtrage (WHERE)
        self.filter = []

        # Regroupements (GROUP BY)
        # PostgreSQL est pointilleux sur les colonnes qui apparaissent
        # dans la clause GROUP BY. Si une colonne apparaît dans ORDER BY,
        # elle doit systématiquement apparaître AUSSI dans GROUP BY.
        self.groupby = [
            StateName.order,
            Event.timestamp,
            CorrEvent.ack,
            CorrEvent.priority,
            StateName.statename,
        ]

        self.req = DBSession
        self.plugin = []
        self.events = []

        # Si l'utilisateur est privilégié, il a accès
        # à tous les hôtes/services sans restriction.
        if config.is_manager.is_met(request.environ):
            # Sélection de tous les services de la BDD.
            lls_query = DBSession.query(
                LowLevelService.idservice.label("idsupitem"),
                LowLevelService.servicename.label("servicename"),
                Host.name.label("hostname"),
                Host.address.label("address"),
            ).join(
                (Host, Host.idhost == LowLevelService.idhost),
            ).distinct()

            # Sélection de tous les hôtes de la BDD.
            host_query = DBSession.query(
                Host.idhost.label("idsupitem"),
                expr_null().label("servicename"),
                Host.name.label("hostname"),
                Host.address.label("address"),
            ).distinct()

            # Application des filtres des plugins si nécessaire.
            if search is not None:
                # On tire ici partie du fait que les listes sont passées
                # par référence dans les fonctions.
                subqueries = [lls_query, host_query]
                for _plugin, instance in config.get('columns_plugins', []):
                    instance.handle_search_fields(
                        self, search, INNER, subqueries)
                lls_query = subqueries[0]
                host_query = subqueries[1]

            # Union des deux sélections précédentes
            self.items = union_all(
                lls_query,
                host_query,
                correlate=False
            ).alias()

        # Sinon, on ne récupère que les hôtes/services auquel il a accès.
        else:
            items = DBSession.query(
                UserSupItem.idsupitem,
                UserSupItem.servicename,
                UserSupItem.hostname,
                UserSupItem.address,
            ).filter(
                UserSupItem.username == user.user_name
            ).distinct()

            # Application des filtres des plugins si nécessaire.
            if search is not None:
                # On tire ici partie du fait que les listes sont passées
                # par référence dans les fonctions.
                subqueries = [items]
                for _plugin, instance in config.get('columns_plugins', []):
                    instance.handle_search_fields(
                        self, search, INNER, subqueries)
                items = subqueries[0]

            # Permet d'avoir le même format que pour l'autre requête.
            self.items = items.subquery()

        # Tris (ORDER BY)
        # Permet de répondre aux exigences suivantes :
        # - VIGILO_EXIG_VIGILO_BAC_0050
        # - VIGILO_EXIG_VIGILO_BAC_0060
        self.orderby = []
        plugins = config.get('columns_plugins', [])
        if sort:
            for _plugin, instance in plugins:
                criterion = instance.get_sort_criterion(self, sort)
                if criterion is not None:
                    if order == 'asc':
                        self.orderby.append(asc(criterion))
                    else:
                        self.orderby.append(desc(criterion))

        default_sort = aslist(config.get('default_sort', ''))
        for sort_column in default_sort:
            criterion = None
            sort_field, _dummy, sort_order = sort_column.partition(':')
            for _plugin, instance in plugins:
                criterion = instance.get_sort_criterion(self, sort_field)
                if criterion is not None:
                    if sort_order == 'desc':
                        self.orderby.append(desc(criterion))
                    elif sort_order in ('asc', None):
                        self.orderby.append(asc(criterion))
                    else:
                        self.orderby.append(asc(criterion))
                        LOGGER.warn('Invalid sort order: "%s", sorting in '
                                    'ascending order instead', sort_order)
                    break
            if criterion is None:
                LOGGER.info('No such plugin: "%s"', sort_field)

        if search is not None:
            # 2nde passe pour les filtres : self.items est désormais défini.
            for _plugin, instance in plugins:
                instance.handle_search_fields(self, search, ITEMS, subqueries)

        if mask_closed_events:
            self.filter.append(
                # On masque les événements avec l'état OK
                # et traités (ack == CorrEvent.ACK_CLOSED).
                not_(and_(
                    StateName.statename.in_([u'OK', u'UP']),
                    CorrEvent.ack == CorrEvent.ACK_CLOSED
                ))
            )


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

        for plugin in config['columns_plugins']:
            self.add_plugin(plugin)

        # Toutes les requêtes ont besoin de récupérer l'état courant
        # de l'événement.
        self.join.append((StateName, StateName.idstatename == \
                                        Event.current_state))

        # PostgreSQL est pointilleux sur les colonnes qui apparaissent
        # dans la clause GROUP BY. Si une colonne apparaît dans SELECT,
        # elle doit systématiquement apparaître AUSSI dans GROUP BY.
        # Ici, on ajoute automatiquement les colonnes du SELECT au GROUP BY.
        self.add_group_by(*self.table)

        # query et join ont besoin de referrence
        self.req = self.req.query(*self.table)
        self.req = self.req.join(*self.join)
        self.req = self.req.options(*self.option)

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

    def add_option(self, *argv):
        """
        Ajoute une ou plusieurs options à la requête.

        @param argv: Liste des options à ajouter
        """

        # On vérifie qu'il n'y a pas de doublons
        # dans la liste finale des options.

        for i in argv:
            for j in self.option:
                if str(i) == str(j):
                    break
            self.option.append(i)

    def add_contains_eager(self, relation):
        """
        Ajoute une option de type contains_eager à la
        requête pour la relation passée en paramètre.
        """
        self.add_option(contains_eager(relation))

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
        self.events = []

        for data in self.req[first_row : last_row]:
            self.events.append(data)

    def format_history(self):
        """
        Formate les historiques correspondant aux événements sélectionnés
        pour un affichage simple du résultat par Genshi.
        On génère une liste de liste, chaqu'une étant la description
        de l'affichage pour un historique donné.
        """

        ids = [data[0].idevent for data in self.events]
        history = DBSession.query(
                    EventHistory,
                ).filter(EventHistory.idevent.in_(ids)
                ).order_by(desc(EventHistory.timestamp)
                ).order_by(desc(EventHistory.idhistory))
        return history

    def generate_tmpl_context(self):
        """
        Génère et peuple la variable tmpl_context avec les dialogues et
        formulaires nécessaire au fonctionnement de Vigiboard
        """

        from vigiboard.controllers.root import get_last_modification_timestamp

        # Si les objets manipulés sont des Event, on a facilement les idevent.
        if not len(self.events):
            ids = []
        elif isinstance(self.events[0][0], Event):
            ids = [data[0].idevent for data in self.events]
        # Sinon, il s'agit de CorrEvent(s) dont on récupère l'idcause.
        else:
            ids = [data[0].idcause for data in self.events]

        # Ajout des formulaires et préparation
        # des données pour ces formulaires.
        tmpl_context.last_modification = \
            mktime(get_last_modification_timestamp(ids).timetuple())

        tmpl_context.edit_event_form = EditEventForm("edit_event_form",
            submit_text=_('Apply'), action=url('/update'))

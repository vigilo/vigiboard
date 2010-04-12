# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""Gestion de la requête, des plugins et de l'affichage du Vigiboard"""

from time import mktime
from logging import getLogger

from tg import url, config, tmpl_context
from tg.i18n import get_lang
from pylons.i18n import ugettext as _
from paste.deploy.converters import asbool

from sqlalchemy import not_, and_, asc, desc
from sqlalchemy.sql.expression import or_, null as expr_null, union

from vigilo.models.session import DBSession
from vigilo.models.tables import Event, CorrEvent, EventHistory, \
                        Host, LowLevelService, StateName
from vigilo.models.tables.secondary_tables import SUPITEM_GROUP_TABLE
from vigiboard.widgets.edit_event import create_edit_event_form, EditEventForm
from vigiboard.widgets.search_form import create_search_form, SearchForm
from vigiboard.controllers.plugins import VigiboardRequestPlugin

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

    def __init__(self, user, mask_closed_events=True):
        """
        Initialisation de l'objet qui effectue les requêtes de VigiBoard
        sur la base de données.
        Cet objet est responsable de la vérification des droits de
        l'utilisateur sur les données manipulées.
        """

        # TODO: Utiliser le champ "language" du modèle pour cet utilisateur ?
        # On récupère la langue du navigateur de l'utilisateur
        lang = get_lang()
        if not lang:
            lang = config['lang']
        else:
            lang = lang[0]

        # TODO: Il faudrait gérer les cas où tout nous intéresse dans "lang".
        # Si l'identifiant de langage est composé (ex: "fr_FR"),
        # on ne récupère que la 1ère partie.
        lang = lang.replace('_', '-')
        lang = lang.split('-')[0]

        self.user_groups = user.supitemgroups(False)
        self.lang = lang
        self.generaterq = False

        # Sélectionne tous les IDs des services auxquels
        # l'utilisateur a accès.
        lls_query = DBSession.query(
            LowLevelService.idservice.label("idsupitem"),
            LowLevelService.servicename.label("servicename"),
            Host.name.label("hostname"),
            SUPITEM_GROUP_TABLE.c.idgroup.label("idsupitemgroup"),
        ).join(
            (Host, Host.idhost == LowLevelService.idhost),
        ).outerjoin(
            (SUPITEM_GROUP_TABLE,
                or_(
                    SUPITEM_GROUP_TABLE.c.idsupitem == \
                        LowLevelService.idhost,
                    SUPITEM_GROUP_TABLE.c.idsupitem == \
                        LowLevelService.idservice,
                )
            ),
        ).filter(
            SUPITEM_GROUP_TABLE.c.idgroup.in_(self.user_groups)
        )

        # Sélectionne tous les IDs des hôtes auxquels
        # l'utilisateur a accès.
        host_query = DBSession.query(
            Host.idhost.label("idsupitem"),
            expr_null().label("servicename"),
            Host.name.label("hostname"),
            SUPITEM_GROUP_TABLE.c.idgroup.label('idsupitemgroup'),
        ).join(
            (SUPITEM_GROUP_TABLE, SUPITEM_GROUP_TABLE.c.idsupitem == \
                Host.idhost),
        ).filter(
            SUPITEM_GROUP_TABLE.c.idgroup.in_(self.user_groups),
        )

        # Objet Selectable renvoyant des informations sur un SupItem
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
        self.filter = []
        if mask_closed_events:
            self.filter.append(
                # On masque les événements avec l'état OK
                # et traités (status == u'AAClosed').
                not_(and_(
                    StateName.statename.in_([u'OK', u'UP']),
                    CorrEvent.status == u'AAClosed'
                ))
            )

        # Permet de définir le sens de tri pour la priorité.
        if config['vigiboard_priority_order'] == 'asc':
            priority_order = asc(CorrEvent.priority)
        else:
            priority_order = desc(CorrEvent.priority)

        # Tris (ORDER BY)
        # Permet de répondre aux exigences suivantes :
        # - VIGILO_EXIG_VIGILO_BAC_0050
        # - VIGILO_EXIG_VIGILO_BAC_0060
        self.orderby = [
            desc(CorrEvent.status),                         # État acquittement
            asc(StateName.statename.in_([u'OK', u'UP'])),   # Vert / Pas vert
            priority_order,                                 # Priorité ITIL
        ]

        if asbool(config.get('state_first', True)):
            self.orderby.extend([
                desc(StateName.order),                      # Etat courant
                desc(Event.timestamp),                      # Timestamp
            ])
        else:
            self.orderby.extend([
                desc(Event.timestamp),                      # Timestamp
                desc(StateName.order),                      # Etat courant
            ])


        # Regroupements (GROUP BY)
        # PostgreSQL est pointilleux sur les colonnes qui apparaissent
        # dans la clause GROUP BY. Si une colonne apparaît dans ORDER BY,
        # elle doit systématiquement apparaître AUSSI dans GROUP BY.
        self.groupby = [
            StateName.order,
            Event.timestamp,
            CorrEvent.status,
            CorrEvent.priority,
            StateName.statename,
        ]

        self.plugin = []
        self.events = []
        self.req = DBSession

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
                    'vigiboard.controllers.plugins.' +\
                            plug[0], globals(), locals(), [plug[1]], -1)
                self.add_plugin(getattr(mypac, plug[1])())
            except ImportError:
                # On loggue l'erreur et on ignore le plugin.
                LOGGER.error(_('No such plugin "%s"') % plug[0])

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
        Génère et peuple la variable tmpl_context avec les Dialogs et
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

        tmpl_context.calendar_lang = self.lang
        # TRANSLATORS: Format de date et heure compatible Python/JavaScript.
        tmpl_context.calendar_date_format = _('%Y-%m-%d %I:%M:%S %p')

        tmpl_context.edit_event_form = create_edit_event_form
        tmpl_context.search_form = create_search_form


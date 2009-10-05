# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""Gestion de la requête, des plugins et de l'affichage du Vigiboard"""

from vigiboard.model import Event, EventsAggregate, EventHistory, \
        Host, HostGroup, Service, ServiceGroup
from tg import tmpl_context, url, config
from vigiboard.model import DBSession
from sqlalchemy import not_, and_, asc, desc, sql
from tw.jquery.ui_dialog import JQueryUIDialog
from vigiboard.widgets.edit_event import EditEventForm , SearchForm
from vigiboard.controllers.vigiboard_plugin import VigiboardRequestPlugin
from pylons.i18n import ugettext as _

class VigiboardRequest():
    
    """
    Classe gérant la génération de la requête finale,
    le préformatage des évènements et celui des historiques
    """

    def __init__(self, user):

        """
        Initialisation de toutes les variables nécessaires: Liste des groupes
        de l'utilisateur, les classes à appliquer suivant la sévérité, les
        différentes étapes de la génération de la requête et la liste des
        plugins appliqués.
        """

        self.user_groups = user.groups

        self.bouton_severity = (
                'Minor', 'Minor', 'Minor', 'Minor',
                'Minor', 'Minor', 'Major', 'Critical'
            )

        self.class_severity = (
                'None', 'None', 'None', 'None',
                'None', 'Minor', 'Major', 'Critical'
            )

        self.severity = (
                _('None'),          # 0
                _('OK'),
                _('Suppressed'),
                _('Initial'),
                _('Maintenance'),
                _('Minor'),
                _('Major'),
                _('Critical'),      # 7
            )

        self.class_ack = {
                'Acknowledged': 'Ack',
                'None': '',
                'AAClosed': 'Ack'
            }

        self.generaterq = False

        self.table = [
            EventsAggregate,
            sql.func.count(EventsAggregate.idaggregate)
        ]

        self.join = [
                (Event, EventsAggregate.idcause == Event.idevent),
                (Host, Event.hostname == Host.name),
                (Service, Event.servicename == Service.name),
                (HostGroup, Host.name == HostGroup.hostname),
                (ServiceGroup, Service.name == ServiceGroup.servicename),
            ]

        self.outerjoin = []

        self.filter = [
                HostGroup.groupname.in_(self.user_groups),
                ServiceGroup.groupname.in_(self.user_groups),
                not_(and_(Event.active == False,
                    EventsAggregate.status == u'AAClosed')),
                EventsAggregate.timestamp_active != None#,
                #not_(Event.timestamp_active.like('0000-00-00 00:00:00'))
            ]

        self.orderby = [
                desc(EventsAggregate.status),
                desc(Event.active),
                desc(EventsAggregate.severity),
                asc(Event.hostname),
                desc(Event.timestamp),
            ]

        self.groupby = [
                EventsAggregate.idaggregate,
                EventsAggregate,
                Event.active,
                Event.hostname,
                Event.timestamp,
            ]

        self.plugin = []
        self.events = []
        self.idevents = []
        self.hist = []
        self.req = DBSession
        self.context_fct = []

    def get_bouton_severity(self, severity):
        if severity is None:
            return 'Unknown'
        return self.bouton_severity[severity]

    def add_plugin(self, *argv):

        """
        Ajout d'un plugin, on lui prélève ses ajouts dans la requête
        """
        for i in argv :
            if isinstance(i, VigiboardRequestPlugin):
                if i.table :
                    self.add_table(*i.table)
                if i.join :
                    self.add_join(*i.join)
                if i.outerjoin :
                    self.add_outer_join(*i.outerjoin)
                if i.filter :
                    self.add_filter(*i.filter)
                if i.groupby :    
                    self.add_group_by(*i.groupby)
                if i.orderby :
                    self.add_order_by(*i.orderby)
                self.plugin.append(i)

    def generate_request(self):
        
        """
        Génération de la requête avec l'ensemble des données stockées
        et la place dans la variable rq de la classe
        """
        for plug in config.get('vigiboard_plugins', []):
            try:
                mypac = __import__(
                    'vigiboard.controllers.vigiboard_plugin.' +\
                            plug[0], globals(), locals(), [plug[1]], -1)
                self.add_plugin(getattr(mypac, plug[1])())
            except:
                raise

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

    def num_rows(self):

        """
        Retourne le nombre de lignes de la requête.
        Si celle-ci n'est pas encore générée, on le fait.

        @return: Nombre de ligne
        """

        if not self.generaterq:
            self.generate_request()
            self.generaterq = True
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
                if str(i) == str(j):
                    break
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

    def format_events_img_status(self, event):
        
        """
        Suivant l'état de l'évènement, retourne la classe à appliquer
        à l'image indiquant si l'évènement est pris en compte ou non.

        @param event: l'évènement à analyser

        @return: Dictionnaire représentant la classe à appliquer
        """

        if event.cause.active and event.status == 'AAClosed':
            return { 'src': url('/images/crossed.png') }
        elif event.status == 'Acknowledged' :
            return { 'src': url('/images/checked.png') }
        else:
            return None

    def format_events(self, first_row, last_row):
        """
        Formate la réponse de la requête et y applique les plugins
        pour un affichage simple du résultat par Genshi.
        On génère une liste de liste, chaqu'une étant la description de
        l'affichage pour un évènement donné.

        @param first_row: Indice de début de la liste des évènements
        @param last_row: Indice de fin de la liste des évènements
        """
        
        # Si la requête n'est pas générée, on le fait
        if not self.generaterq :
            self.generate_request()
            self.generaterq = True

        # Liste des éléments pour la tête du tableau

        lst_title = [
                ['',{}],
                [_('Date')+ '<span style="font-weight:normal">' + \
                        '<br />['+_('Duration') + ']</span>',
                        {'style':'text-align:left'}],
                ['#', {'title':_('Occurrence count')}],
                [_('Host'), {'style':'text-align:left'}],
                [_('Service Type')+'<br />'+_('Service Name'),
                    {'style':'text-align:left'}], 
                [_('Output'), {'style':'text-align:left'}]
                ]
        lst_title.extend([[plug.name, plug.style] for plug in self.plugin])
        lst_title.extend([['['+_('TT')+']', {'title': _('Trouble Ticket')}],
                            ['', {}]])
        events = [lst_title]
        i = 0
        class_tr = ['odd', 'even']
        ids = []
        for req in self.req[first_row : last_row]:
            # Si il y a plus d'un élément dans la liste des tables,
            # req devient une liste plutôt que d'être directement la
            # table souhaitée

            if isinstance(req, EventsAggregate):
                event = req
            else:
                event = req[0]
            ids.append(event.idcause)

            # La liste pour l'évènement actuel comporte dans l'ordre :
            #   L'évènement en lui-même
            #   La classe à appliquer sur la ligne (permet d'alterner les
            #       couleurs suivant les lignes)
            #   La classe pour la case comportant la flèche de détails
            #   La classe pour la date, l'occurence et l'édition
            #   L'image à afficher pour la flèche de détails
            #   Une liste (une case par plugin) de ce que le plugin souhaite
            #       afficher en fonction de l'évènement

            if event.cause.active:
                events.append([
                        event,
                        {'class': class_tr[i % 2]},
                        {'class': self.get_bouton_severity(event.severity) + \
                            self.class_ack[event.status]},
                        {'class': self.get_bouton_severity(event.severity) + \
                            self.class_ack[event.status]},
                        {'src': '/images/%s2.png' % \
                            self.get_bouton_severity(event.severity).upper()},
                        self.format_events_img_status(event),
                        [[j.__show__(event), j.style] for j in self.plugin]
                    ])

            else:
                events.append([
                        event,
                        {'class': class_tr[i % 2]},
                        {'class': self.get_bouton_severity(event.severity) + \
                            self.class_ack[event.status] },
                        {'class': 'Cleared' + self.class_ack[event.status]},
                        {'src': '/images/%s2.png' % \
                            self.get_bouton_severity(event.severity).upper()},
                        self.format_events_img_status(event),
                        [[j.__show__(event), j.style] for j in self.plugin]
                    ])
            i += 1

        # On sauvegarde la liste précédemment créée puis on remplit
        # le TmplContext
        self.events = events
        self.idevents = ids

    def format_history(self):
        
        """
        Formate les historiques correspondant aux évènements sélectionnés
        pour un affichage simple du résultat par Genshi.
        On génère une liste de liste, chaqu'une étant la description
        de l'affichage pour un historique donné.
        """

        history = DBSession.query(EventHistory
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
        hist_tmp = []
        last_idevent = history[0].idevent
        for hist in history :
            
            if last_idevent != hist.idevent:
                hists[last_idevent] = hist_tmp
                last_idevent = hist.idevent
                hist_tmp = []

            # La liste pour l'historique actuel comporte dans l'ordre :
            #   Le moment où il a été généré
            #   Qui l'a généré
            #   Le type d'action qui a été appliqué
            #   La sévérité de l'action si besoin est
            #   Le détail de l'action
            #   La classe à appliquer à la ligne (permet d'alterner
            #       les couleurs)
            #   La classe de la sévérité s'il y a

            if hist.value :
                hist_tmp.append([
                    hist.timestamp,
                    hist.username,
                    hist.type_action,
                    self.severity[min(int(hist.value), 7)],
                    hist.text,
                    {'class': class_tr[i % 2]},
                    {'class': self.class_severity[min(int(hist.value), 7)]}
                ])

            else:
                hist_tmp.append([
                    hist.timestamp,
                    hist.username,
                    hist.type_action,
                    self.severity[0],
                    hist.text,
                    {'class': class_tr[i % 2]},
                    {'class': self.class_severity[0]}
                ])    
            i += 1
        
        hists[last_idevent] = hist_tmp
        self.hist = hists

    def generate_tmpl_context(self):
        
        """
        Génère et peuple la variable tmpl_context avec les Dialogs et
        formulaires nécessaire au fonctionnement de Vigiboard
        """

        # Dialogue d'édition
        tmpl_context.edit_event_form = EditEventForm('edit_event_form',
                action=url('/update'))
        tmpl_context.edit_eventdialog = JQueryUIDialog(id='Edit_EventsDialog',
                autoOpen=False,title=_('Edit Event'))
    
        # Dialogue de recherche
        tmpl_context.search_form = SearchForm('search_form',
                action=url('/'))
        tmpl_context.searchdialog = JQueryUIDialog(id='SearchDialog',
                autoOpen=False, title=_('Search Event'))
        
        # Dialogue de détail d'un évènement
        tmpl_context.historydialog = JQueryUIDialog(id='HistoryDialog',
                autoOpen=False, title=_('History'))

        # Exécution des contexts des plugins
        for j in self.plugin:
            j.context(self.context_fct)


# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2007-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Gère la planification des mises en silence."""

#import time
from datetime import datetime

from tg import expose, validate, require, flash, tmpl_context, \
    request, config, redirect
from tg.i18n import lazy_ugettext as l_, ugettext as _
from tg.support import paginate
from tg.predicates import Any, All, in_group, \
                                    has_permission, not_anonymous
from formencode import validators, schema
from formencode.compound import All as All_
from formencode.foreach import ForEach
from sqlalchemy.exc import InvalidRequestError, IntegrityError
from sqlalchemy.sql.expression import asc, desc

from vigilo.turbogears.helpers import get_current_user
from vigilo.turbogears.controllers import BaseController
from vigilo.models.session import DBSession
from vigilo.models.tables import SupItem, Host, LowLevelService, \
                            HighLevelService, StateName, Silence, UserSupItem
from vigilo.models.tables.secondary_tables import SILENCE_STATE_TABLE
from vigilo.models.utils import group_concat

from vigiboard.lib import error_handler

import logging

LOGGER = logging.getLogger(__name__)

__all__ = ['SilenceController']

# pylint: disable-msg=R0201
class SilenceController(BaseController):
    """
    Contrôleur gérant la planification des mises en silence.
    """

    # Prédicat pour la restriction de l'accès aux interfaces.
    # L'utilisateur doit avoir la permission "vigiboard-silence"
    # ou appartenir au groupe "managers" pour accéder à VigiBoard.
    access_restriction = All(
        not_anonymous(msg=l_("You need to be authenticated")),
        Any(in_group('managers'),
            has_permission('vigiboard-silence'),
            msg=l_("Insufficient privileges for this action"))
    )

    def process_form_errors(self, *argv, **kwargv):
        """
        Gestion des erreurs de validation : on affiche les erreurs
        puis on redirige vers la dernière page accédée.
        """
        for k in tmpl_context.form_errors:
            flash("'%s': %s" % (k, tmpl_context.form_errors[k]), 'error')
        redirect(request.environ.get('HTTP_REFERER', '/'))

    def query_silences(self):
        """
        Retourne une requête SQLAlchemy interrogeant
        la table des mises en silence
        """

        # Si l'utilisateur fait partie du groupe 'managers', on récupère la
        # liste de tous les supitems de la base de données
        if in_group('managers').is_met(request.environ):
            lls_query = DBSession.query(
                    LowLevelService.idservice.label('idsupitem'),
                    LowLevelService.servicename.label("servicename"),
                    Host.name.label('hostname')
                ).join((Host, Host.idhost == LowLevelService.idhost))

            host_query = DBSession.query(
                    Host.idhost.label('idsupitem'),
                    "NULL",
                    Host.name.label('hostname')
                )

            supitems = lls_query.union(host_query).subquery()

        # Sinon on ne récupère que les supitems auxquels l'utilisateurs a accès
        else:
            user_name = request.identity['repoze.who.userid']
            supitems = DBSession.query(
                UserSupItem.idsupitem.label('idsupitem'),
                UserSupItem.servicename.label("servicename"),
                UserSupItem.hostname.label('hostname')
            ).filter(
                UserSupItem.username == user_name
            ).distinct().subquery()

        # On interroge la base pour avoir la liste des règles de mise en silence
        # correspondant à ces supitems.
        states = DBSession.query(
                StateName.statename,
                SILENCE_STATE_TABLE.c.idsilence,
            ).join((SILENCE_STATE_TABLE,
                StateName.idstatename == SILENCE_STATE_TABLE.c.idstate)
            ).order_by(StateName.statename
            ).subquery()
        states = DBSession.query(
                states.c.idsilence,
                group_concat(states.c.statename, ', ').label('states'),
            ).group_by(states.c.idsilence
            ).subquery()
        silences = DBSession.query(
                Silence,
                supitems.c.hostname,
                supitems.c.servicename,
                states.c.states
            ).join((supitems, supitems.c.idsupitem == Silence.idsupitem)
            ).join((states, states.c.idsilence == Silence.idsilence))

        return silences

    def check_silence_rule_existence(self, idsupitem):
        """
        S'assure qu'aucune règle de mise en silence n'existe dans la base de
        données pour le supitem considéré, et affiche un message d'erreur dans
        le cas contraire.

        @param idsupitem: Identifiant du supitem.
        @type  idsupitem: C{int}
        """
        silence = DBSession.query(Silence
            ).filter(Silence.idsupitem == idsupitem
            ).first()
        if not silence:
            return
        if isinstance(silence.supitem, LowLevelService):
            msg = _("Another rule already exists for service '%s' " \
                    "on host '%s'.") % (silence.supitem.servicename,
                        silence.supitem.host.name)
        else:
            msg = _("Another rule already exists for host '%s'.") % (
                silence.supitem.name)
        error_handler.handle_error_message(msg)

    class IndexSchema(schema.Schema):
        """Schéma de validation de la méthode index."""
        # Si on ne passe pas le paramètre "page" ou qu'on passe une valeur
        # invalide ou pas de valeur du tout, alors on affiche la 1ère page.
        page = validators.Int(min=1, if_missing=1,
            if_invalid=1, not_empty=True)
        sort = validators.OneOf(
            ['hostname', 'servicename', 'lastmodification',
                'author', 'comment', 'states'],
            if_missing='lastmodification', if_invalid='lastmodification')
        order = validators.OneOf(['desc', 'asc'],
            if_missing='desc', if_invalid='desc')

    @validate(
        validators=IndexSchema(),
        error_handler = process_form_errors)
    @expose('silence.html')
    @require(access_restriction)
    def index(self, page=1, sort=None, order=None):
        """
        Affiche la liste des règles de mise en silence enregistrées dans
        la BDD, que l'utilisateur pourra ensuite éditer ou supprimer.

        @param sort: (optionnel) Critère de tri de la liste des
                     règles de mise en silence enregistrées.
        @type  sort: C{str}
        @param order: (optionnel) Ordre de tri.
        @type  order: C{str}
        """

#        # On récupère la langue de l'utilisateur
#        lang = get_lang()
#        if not lang:
#            lang = ['fr']
#        lang = lang[0]

        # On récupère tous les enregistrements de la table
        # silence, qu'ils concernent des hôtes, des services
        # de bas niveau, ou bien des services de haut niveau.
        silences = self.query_silences()

        # On trie ces enregistrements selon le critère choisi
        # par l'utilisateur (par défaut, la date d'ajout).
        sort_keys = {
            'hostname': 'hostname',
            'servicename': 'servicename',
            'lastmodification': Silence.lastmodification,
            'author': Silence.author,
            'comment': Silence.comment,
#            'start': Silence.start,
#            'end': Silence.end,
            'states': 'states',
        }
        if sort in sort_keys.keys():
            # Tri dans l'ordre croissant
            if order != 'desc':
                silences = silences.order_by(asc(sort_keys[sort]))
            # Tri dans l'ordre décroissant
            else:
                silences = silences.order_by(desc(sort_keys[sort]))

        # On calcule la pagination
        page = paginate.Page(silences, page=page,
            items_per_page=int(config['vigiboard_items_per_page']))

#        # On initialise les widgets des calendriers
#        # utilisés dans le formulaire de mise en silence.
#        start_calendar = CalendarDateTimePicker('start',
#                                            button_text = l_("Choose a date"),
#                                            date_format = '%Y-%m-%d %H:%M',
#                                            calendar_lang = lang)
#        end_calendar = CalendarDateTimePicker('end',
#                                            button_text = l_("Choose a date"),
#                                            date_format = '%Y-%m-%d %H:%M',
#                                            calendar_lang = lang)

        # Traduction du nom des colonnes
        columns = [
            ('hostname', l_('Host')),
            ('servicename', l_('Service')),
            ('states', l_('States')),
            ('lastmodification', l_('Last modification')),
            ('author', l_('Author')),
            ('comment', l_('Comment'))
        ]

        return dict(
            page=page,
            sort=sort,
            order=order,
#            start_calendar=start_calendar,
#            end_calendar=end_calendar,
            columns=columns
        )

    @expose('silence_form.html')
    @require(access_restriction)
    def add(self):
        """
        Affiche un formulaire d'ajout d'une règle de mise en silence.
        """
        return dict(
            id=None,
            hostname=None,
            servicename=None,
            states=None,
            comment=None,
#            start_calendar=start_calendar,
#            end_calendar=end_calendar,
        )

    class UpdateSchema(schema.Schema):
        """Schéma de validation de la méthode update."""
        id = validators.Int(min=1, not_empty=True)

    @validate(
        validators=UpdateSchema(),
        error_handler = process_form_errors)
    @expose('silence_form.html')
    @require(access_restriction)
    def update(self, id):
        """
        Affiche un formulaire de mise à jour d'une règle de mise en silence.

        @param id: Identifiant de la règle.
        @type  id: C{int}
        """

        # On s'assure que la règle existe bien dans la base
        try:
            silence = DBSession.query(Silence
                ).filter(Silence.idsilence == id).one()
        except InvalidRequestError as e:
            msg = _('An exception has been raised while ' \
                    'querying the database: %s') % str(e)
            error_handler.handle_error_message(msg)
        if not silence:
            msg = _("Silence rule #%s does not exist.") % id
            error_handler.handle_error_message(msg)

        # On s'assure que l'utilisateur dispose bien des permissions sur le
        # supitem considéré
        user = get_current_user()
        if not silence.supitem.is_allowed_for(user):
            msg = _("Silence rule #%s does not exist.") % id
            error_handler.handle_error_message(msg)

        if hasattr(silence.supitem, 'servicename'):
            hostname = silence.supitem.host.name
            servicename = silence.supitem.servicename
        else:
            hostname = silence.supitem.name
            servicename = None

        return dict(
            id=id,
            hostname=hostname,
            servicename=servicename,
            states=[s.statename for s in silence.states],
            comment=silence.comment,
#            start_calendar=start_calendar,
#            end_calendar=end_calendar,
        )

    class CreateOrModifySchema(schema.Schema):
        """Schéma de validation de la méthode create_or_modify."""
        states = All_(
            validators.Set(use_set=True),
            validators.OneOf(["WARNING", "CRITICAL", "DOWN", "UNKNOWN"],
                testValueList=True, hideList=True, not_empty=True)
        )
        host = validators.String(not_empty=True)
        service = validators.String()
        comment = validators.String()
        idsilence = validators.Int(min=1, if_missing=None,
            if_invalid=None, not_empty=False)

    @validate(
        validators=CreateOrModifySchema(),
        error_handler = process_form_errors)
    @expose()
    @require(access_restriction)
    def create_or_modify(
            self,
            states,
            host,
            service=None,
#            start=time.time(),
#            end=time.time(),
            comment=None,
            idsilence=None):
        """
        Ajoute une règle de mise en silence d'un hôte/service,
        ou en modifie une déjà existante.

        @param states: (optionnel) Liste des états concernés par la règle.
        @type  states: C{list} of C{unicode}
        @param host: Nom de l'hôte sur lequel porte la règle.
        @type  host: C{unicode}
        @param service: (optionnel) Nom du service sur lequel
            porte la règle.
        @type  service: C{unicode}
#        @param start: Début de la mise en silence planifiée.
#        @type  start: C{str}
#        @param end: Fin de la mise en silence planifiée.
#        @type  end: C{str}
        @param comment: (optionnel) Commentaire accompagnant la règle.
        @type  comment: C{unicode}
        @param idsilence: (optionnel) Identifiant de la règle dans le cas d'une
            mise à jour.
        @type  idsilence: C{int}
        """

        # TODO: Faire ce traitement dans le schéma de validation
        if not states:
            msg = _('No state specified for the silence rule.')
            error_handler.handle_error_message(msg)
        states = list(states)

        # On récupère le nom et l'IP de l'utilisateur.
        user = get_current_user()
        user_name = user.user_name
        user_ip = request.remote_addr

        # On récupère l'identifiant de l'item (hôte
        # ou service) concerné par la mise en silence.
        idsupitem = SupItem.get_supitem(host, service)
        if idsupitem:
            try:
                supitem = DBSession.query(SupItem
                    ).filter(SupItem.idsupitem == idsupitem).one()
            except InvalidRequestError as e:
                msg = _('An exception has been raised while ' \
                        'querying the database: %s') % str(e)
                error_handler.handle_error_message(msg)
        if not idsupitem or not supitem.is_allowed_for(user):
            if not service:
                msg = _("Host '%s' does not exist.") % host
                error_handler.handle_error_message(msg)
            else:
                msg = _("Service '%s' does not exist for host '%s'."
                    ) % (service, host)
                error_handler.handle_error_message(msg)

        # On distingue mise à jour et création :

        # 1. Dans le cas d'une mise à jour :
        if idsilence:

            # - On s'assure que la règle existe bien dans la base
            try:
                silence = DBSession.query(Silence
                    ).filter(Silence.idsilence == idsilence).one()
            except InvalidRequestError as e:
                msg = _('An exception has been raised while ' \
                        'querying the database: %s') % str(e)
                error_handler.handle_error_message(msg)
            if not silence:
                msg = _("Silence rule #%s does not exist.") % idsilence
                error_handler.handle_error_message(msg)

            # - Si le supitem a été modifié, on vérifie qu'aucune
            #   autre règle n'existe pour le nouveau supitem
            if silence.idsupitem != idsupitem:
                self.check_silence_rule_existence(idsupitem)

            # On supprime les états existants
            silence.states = []

        # 2. Dans le cas d'une création :
        else:

            # - On s'assure qu'aucune autre règle n'existe pour le supitem
            self.check_silence_rule_existence(idsupitem)

            # - Et on crée l'objet représentant la règle
            silence = Silence()

        # Dans les 2 cas, on met à jour l'objet avec
        # les informations passées en paramètre
        silence.idsupitem = idsupitem
        silence.comment = comment
        silence.lastmodification = datetime.utcnow().replace(microsecond=0)
        silence.author = user_name
        try:
            DBSession.add(silence)
            for state in states:
                s = DBSession.query(StateName
                    ).filter(StateName.statename == state).one()
                silence.states.append(s)
            DBSession.flush()
        except (IntegrityError, InvalidRequestError) as e:
            msg = _('An exception has been raised while ' \
                    'updating the database: %s') % str(e)
            error_handler.handle_error_message(msg)

        # On notifie l'opération dans les logs, on affiche un message de
        # succès, et on redirige le navigateur vers la liste des règles de
        # mise en silence.
        if idsilence:
            # Mise à jour d'une règle portant sur un service
            if hasattr(silence.supitem, 'servicename'):
                LOGGER.info(_(
                    'User %(user)s (IP: %(ip)s) updated silence rule ' \
                    '#%(id)s for service %(service)s on host %(host)s.'
                ) % {
                    'user': user_name,
                    'ip': user_ip,
                    'id': idsilence,
                    'host': host,
                    'service': service
                })
                flash(_(
                    'Silence rule #%(id)s (host: %(host)s, service: ' \
                    '%(service)s) has been successfully updated.') % {
                        'id': idsilence,
                        'host': host,
                        'service': service
                })
            # Mise à jour d'une règle portant sur un hôte
            else:
                LOGGER.info(_(
                    'User %(user)s (IP: %(ip)s) updated silence rule ' \
                    '#%(id)s for host %(host)s.') % {
                        'user': user_name,
                        'ip': user_ip,
                        'id': idsilence,
                        'host': host
                })
                flash(_(
                    'Silence rule #%(id)s (host: %(host)s) ' \
                    'has been successfully updated.') % {
                        'id': idsilence,
                        'host': host
                })
        else:
            # Ajout d'une règle portant sur un service
            if service:
                LOGGER.info(_(
                    'User %(user)s (IP: %(ip)s) added a silence rule (#' \
                    '%(id)s) for service %(service)s on host %(host)s.'
                ) % {
                    'user': user_name,
                    'ip': user_ip,
                    'id': idsilence,
                    'host': host,
                    'service': service
                })
                flash(_('A new silence rule (#%(id)s) has been added for '
                    'service "%(service)s" on host "%(host)s".') % {
                        'id': silence.idsilence,
                        'service': service,
                        'host': host
                    })
            # Ajout d'une règle portant sur un hôte
            else:
                LOGGER.info(_(
                    'User %(user)s (IP: %(ip)s) added a silence rule ' \
                    '(#%(id)s) for host %(host)s.') % {
                        'user': user_name,
                        'ip': user_ip,
                        'id': idsilence,
                        'host': host
                })
                flash(_('A new silence rule (#%(id)s) has been added for the '
                    'host "%(host)s".') % {
                        'id': silence.idsilence,
                        'host': host
                    })
        redirect('./')


    class DeleteSchema(schema.Schema):
        """Schéma de validation de la méthode delete."""
        id = All_(
            validators.Set(use_set=True),
            ForEach(validators.Int(min=1)),
        )

    @validate(
        validators=DeleteSchema(),
        error_handler = process_form_errors)
    @expose()
    @require(access_restriction)
    def delete(self, id):
        """
        Suppression d'une règle ou d'une liste de règles de mise en silence.

        @param id: Liste des identifiants des règles à supprimer.
        @type  id: C{list} of C{int}
        """

        # TODO: Faire ce traitement dans le schéma de validation
        if not id:
            msg = _('No silence rule id specified.')
            error_handler.handle_error_message(msg)
        id = list(id)

        # On recherche les règles dans la BDD.
        try:
            silences = DBSession.query(Silence
                ).filter(Silence.idsilence.in_(id)).all()
        except InvalidRequestError as e:
            msg = _('An exception has been raised while ' \
                    'querying the database: %s') % str(e)
            error_handler.handle_error_message(msg)

        # On s'assure que toutes les règles ont bien été trouvées dans la
        # base, faute de quoi on lève une erreur et on arrête le traitement
        if len(silences) != len(id):
            missing_ids = [
                i for i in id if i not in [s.idsilence for s in silences]]
            if len(missing_ids) > 1:
                msg = _('Error: the following silence rules do not exist:' \
                    ' %s.') % ", ".join('#' + str(i) for i in missing_ids)
            else:
                msg = _('Error: silence rule #%s does not exist.'
                    ) % ", ".join(str(i) for i in missing_ids)
            error_handler.handle_error_message(msg)

        # On s'assure que l'utilisateur dispose bien des permissions nécessaires
        # pour supprimer chacune des règles
        user = get_current_user()
        for s in silences:
            if not s.supitem.is_allowed_for(user):
                msg = _("Silence rule #%s does not exist.") % s.idsilence
                error_handler.handle_error_message(msg)

        # On supprime les règles dans la BDD.
        try:
            for silence in silences:
                DBSession.delete(silence)
            DBSession.flush()
        except InvalidRequestError as e:
            msg = _('An exception has been raised while ' \
                    'deleting the silence rules: %s') % str(e)
            error_handler.handle_error_message(msg)

        # On notifie l'opération dans les logs
        user_name = user.user_name
        user_ip = request.remote_addr
        for s in silences:
            # Règle concernant un service de bas niveau
            if hasattr(s.supitem, 'servicename'):
                LOGGER.info(_(
                    'User %(user)s (IP: %(ip)s) deleted silence rule ' \
                    '#%(id)s for service %(service)s on host ' \
                    '%(host)s') % {
                        'user': user_name,
                        'ip': user_ip,
                        'id': s.idsilence,
                        'host': s.supitem.host.name,
                        'service': s.supitem.servicename
                })
            # Règle concernant un hôte
            else:
                LOGGER.info(_(
                    'User %(user)s (IP: %(ip)s) deleted silence rule ' \
                    '#%(id)s for host %(host)s') % {
                        'user': user_name,
                        'ip': user_ip,
                        'id': s.idsilence,
                        'host': s.supitem.name,
                })

        # On affiche un message de succès
        if len(id) > 1:
            flash(_('The following silence rules have been successfully ' \
                'deleted: %s.') % ", ".join(str(i) for i in id))
        else:
            flash(_('Silence rule #%s has been successfully ' \
                'deleted.') % id[0])

        # On redirige le navigateur vers la page d'index
        redirect('./', )


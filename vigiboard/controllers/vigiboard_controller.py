# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""
Controller for authentification
"""

from tg import expose, flash, request, redirect

from pylons.i18n import ugettext as _

from vigilo.models import ApplicationLog

from vigiboard.lib.base import BaseController
from vigiboard.controllers.error import ErrorController

# pylint: disable-msg=R0201
class VigiboardRootController(BaseController):
    """
    The root controller for the vigiboard application.
    
    All the other controllers and WSGI applications should be mounted on this
    controller. For example::
    
        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()
    
    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.
    """

    error = ErrorController()

    @expose('login.html')
    def login(self, came_from='/'):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from='/'):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.
        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect('/login', came_from=came_from, __logins=login_counter)
        userid = request.identity['repoze.who.userid']
        ApplicationLog.add_login(userid, request.remote_addr, u'Vigiboard')
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from='/'):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.
        """
        # XXX Ne fonctionne pas, l'identité est déjà oubliée arrivé ici.
#        userid = request.identity['repoze.who.userid']
#        ApplicationLog.add_logout(userid, request.remote_addr, u'Vigiboard')
        flash(_('We hope to see you soon!'))
        redirect(came_from)


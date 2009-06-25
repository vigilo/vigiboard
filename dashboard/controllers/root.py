# -*- coding: utf-8 -*-
"""Main Controller"""

import tg
from tg import expose, flash, require, url, request, redirect, validate, tmpl_context

from tw.forms import validators 

from sets import Set

import pylons
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from catwalk.tg2 import Catwalk
from repoze.what import predicates

from sqlalchemy import not_ , and_ , asc , desc, or_

from tw.jquery import JQueryUIDialog

from dashboard.lib.base import BaseController
from dashboard.model import DBSession, metadata
from dashboard.controllers.error import ErrorController
from dashboard import model
from dashboard.controllers.secure import SecureController

from dashboard.model.bdd_dashboard import *
from dashboard.model.auth import Permission
from repoze.what.predicates import Any,not_anonymous

from dashboard.widgets.edit_event import Edit_Event_Form , Search_Form , edit_event_status_options

__all__ = ['RootController']

def GetUserGroups():
	
	gr = DBSession.query(Groups.name).join(
	    ( GroupPermissions , Groups.name == GroupPermissions.groupname ),
	    ( Permission , Permission.permission_id == GroupPermissions.idpermission )
	    ).filter(Permission.permission_name.in_(request.environ.get('repoze.who.identity').get('permissions')))
	  
	lst_grp = Set([i.name for i in gr])
	lst_tmp = lst_grp
	  
	while len(lst_tmp) > 0:
		gr = DBSession.query(Groups.name).filter(Groups.parent.in_(lst_tmp))
		tmp = Set([])
		for i in gr :
			tmp.add(i.name)
			lst_grp.add(i.name)
		lst_tmp = tmp
	
	return lst_grp

def FormatEventsImgStatu (event):
	if event.active and event.status == 'AAClosed':
		return { 'src': url('/images_vigilo/crossed.png') }
	elif event.status == 'Acknowledged' :
		return { 'src': url('/images_vigilo/checked.png') }
	else:
		return None


def FormatEvents(events,first_row,last_row):
	ev = []
	i=0
	severity = { 0 : 'Minor' , 1 : 'Minor', 2 : 'Minor', 3 : 'Minor', 4 : 'Minor', 5 : 'Minor' , 6 : 'Major' , 7 : 'Critical' }
	class_tr = ['odd','even']
	class_ack = { 'Acknowledged' : 'Ack' , 'None' : '' , 'AAClosed' : 'Ack' }
	ids = []
	for event in events[first_row : last_row]:
		ids.append(event.idevent)
		if event.active :
			ev.append([
				event,
				{'class': class_tr[i%2]},
				{'class' : severity[event.severity] + class_ack[event.status]},
				{'class' : severity[event.severity] + class_ack[event.status] },
				{'src' : url('/images_vigilo/%s2.png' % severity[event.severity].upper())},
				FormatEventsImgStatu(event)
				])
		else :
			ev.append([
				event,
				{'class': class_tr[i%2]},
				{'class' : severity[event.severity] + class_ack[event.status] },
				{'class' : 'Cleared' + class_ack[event.status] },
				{'src' : url('/images_vigilo/%s2.png' % severity[event.severity].upper())},
				FormatEventsImgStatu(event)
				])

		i=i+1
	return ev,ids

def FormatHistory (idevents,hostname,servicename):
	history = DBSession.query(EventHistory).filter(EventHistory.idevent.in_(idevents)).order_by(desc(EventHistory.timestamp))
	severity = { 0 : 'None' , 1 : 'OK', 2 : 'Suppressed', 3 : 'Initial', 4 : 'Maintenance', 5 : 'Minor' , 6 : 'Major' , 7 : 'Critical' }
	hist = []
	i = 0
	class_tr = ['odd','even']
	for h in history :
		if h.value :
			hist.append([
				h.idhistory,
				hostname,
				servicename,
				h.timestamp,
				h.username,
				h.type_action,
				severity[min(int(h.value),7)],
				h.text,
				{'class' : class_tr[i%2]},
				{'class':severity[min(int(h.value),7)]}
			])
		else:
			hist.append([
				h.idhistory,
				hostname,
				servicename,
				h.timestamp,
				h.username,
				h.type_action,
				severity[0],
				h.text,
				{'class' : class_tr[i%2]},
				{'class':severity[0]}
			])	
		i = i+1
	
	return hist

def GenerateTmplContext():
	tmpl_context.edit_eventdialog = JQueryUIDialog(id='Edit_EventsDialog',autoOpen=False,title='Edit Event',width=400)
        tmpl_context.searchdialog = JQueryUIDialog(id='SearchDialog',autoOpen=False,title='Search Event')
        tmpl_context.historydialog = JQueryUIDialog(id='HistoryDialog',autoOpen=False,title='History')
        tmpl_context.edit_event_form = Edit_Event_Form('edit_event_form',action=url('/update_event'))
        tmpl_context.search_form = Search_Form('search_form',action=url('/dashboard'))

class RootController(BaseController):
    """
    The root controller for the dashboard application.
    
    All the other controllers and WSGI applications should be mounted on this
    controller. For example::
    
        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()
    
    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.
    
    """
    secc = SecureController()
    
    admin = Catwalk(model, DBSession)
    
    error = ErrorController()

    @expose('dashboard.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

    @expose('dashboard.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('dashboard.templates.authentication')
    def auth(self):
        """Display some information about auth* on this application."""
        return dict(page='auth')

    @expose('dashboard.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('dashboard.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('dashboard.templates.login')
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)
    
    @expose()
    def post_login(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.
        
        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect(url('/login', came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.
        
        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)

    @expose('dashboard.templates.dashboard')
    @require(Any(not_anonymous(),msg="You need to be authenticated"))
    def dashboard(self,page='1',host=None,service=None,output=None,trouble_ticket=None):
	   try :
	   	page = int(page)
	   except :
		page = 1
	   if page < 1 :
		  page = 1
	   
	   events = DBSession.query(Events).join(
		( Host, Events.hostname == Host.name ),
		( Service, Events.servicename == Service.name ),
		( HostGroups , Host.name == HostGroups.hostname )
		).filter(HostGroups.groupname.in_(GetUserGroups())
		).filter(not_(and_(Events.active == False,Events.status == 'AAClosed'))
		).filter(Events.timestamp_active != None
		).filter(not_(Events.timestamp_active.like('0000-00-00 00:00:00'))
		)

	   if host :
		   events = events.filter(Events.hostname.like('%%%s%%' % host))
	   if service :
		   events = events.filter(Events.servicename.like('%%%s%%' % service))
	   if output :	
		   events = events.filter(Events.output.like('%%%s%%' % output))
	   if trouble_ticket :
		   events = events.filter(Events.trouble_ticket.like('%%%s%%' % trouble_ticket))

	   events= events.order_by(asc(Events.status)
		).order_by(desc(Events.active)
		).order_by(desc(Events.severity)
		).order_by(asc(Events.hostname)
		).order_by(desc(Events.timestamp))

	   total_row = events.count()
	   
	   item_per_page = int(tg.config['dashboard_item_per_page'])

	   if total_row <= item_per_page * (page-1) :
		page = 1
	   id_first_row = item_per_page * (page-1)
	   id_last_row = min(id_first_row + item_per_page,total_row)
	   
	   GenerateTmplContext()
	   events , ids = FormatEvents(events,id_first_row,id_last_row)
	   return dict(
			   events=events,
			   id_first_row=id_first_row,
			   id_last_row=id_last_row,
			   total_row=total_row,
			   pages=range(1,(total_row/item_per_page) + 2),
			   page=page,
			   event_edit_status_options=edit_event_status_options,
			   history=[],
			   hist_error = False
		)
   	
  
    @expose('json')
    def dashboard_HistoryDialog ( self , id ) :
	    events = DBSession.query(Events.severity,Events.idevent,Events.hostname,Events.servicename).filter(Events.idevent == id)[0]
	    initial_state = DBSession.query(EventHistory).filter(EventHistory.idevent == id).order_by(asc(EventHistory.timestamp)).order_by(asc(EventHistory.type_action))
	    if initial_state.count() > 0 :
		    initial_state = initial_state[0].value
	    else :
		    initial_state = 0
	    severity = { 0 : 'None' , 1 : 'OK', 2 : 'Suppressed', 3 : 'Initial', 4 : 'Maintenance', 5 : 'Minor' , 6 : 'Major' , 7 : 'Critical' }
	    return dict(
		initial_state=severity[int(initial_state)],
		current_state=severity[events.severity],
		idevent = events.idevent,
		host = events.hostname,
		service = events.servicename,
		nagios_link = tg.config['dashboard_links.nagios'] % {'idevent':events.idevent},
		metrology_link = tg.config['dashboard_links.metrology'] % {'idevent':events.idevent},
		security_link = tg.config['dashboard_links.security'] % {'idevent':events.idevent},
		servicetype_link = tg.config['dashboard_links.servicetype'] % {'idevent':events.idevent}
		)
	
    @expose('dashboard.templates.dashboard')
    @require(Any(not_anonymous(),msg="You need to be authenticated"))
    def dashboard_event(self,idevent):
	   
	   events = DBSession.query(Events).join(
		( Host, Events.hostname == Host.name ),
		( Service, Events.servicename == Service.name ),
		( HostGroups , Host.name == HostGroups.hostname )
		).filter(HostGroups.groupname.in_(GetUserGroups())
	   	).filter(not_(and_(Events.active == False,Events.status == 'AAClosed'))
		).filter(Events.timestamp_active != None
		).filter(not_(Events.timestamp_active.like('0000-00-00 00:00:00'))
		).filter(Events.idevent == idevent)

	   if events.count() != 1 :
		flash(_('Error in DB'),'error')
		redirect('/dashboard')
	   
   	   GenerateTmplContext()
	   events , ids = FormatEvents(events,0,1)
	   return dict(
			   events=events,
			   id_first_row=1,
			   id_last_row=1,
			   total_row=1,
			   pages=[1],
			   page=1,
			   event_edit_status_options=edit_event_status_options,
			   history=FormatHistory(ids,events[0][0].hostname,events[0][0].servicename),
			   hist_error = True
		)
 	
    @expose('dashboard.templates.dashboard')
    @require(Any(not_anonymous(),msg="You need to be authenticated"))
    def dashboard_host_service(self,host,service):
	   
	   events = DBSession.query(Events).join(
		( Host, Events.hostname == Host.name ),
		( Service, Events.servicename == Service.name ),
		( HostGroups , Host.name == HostGroups.hostname )
		).filter(HostGroups.groupname.in_(GetUserGroups())
	   	).filter(not_(and_(Events.active == False,Events.status == 'AAClosed'))
		).filter(Events.timestamp_active != None
		).filter(not_(Events.timestamp_active.like('0000-00-00 00:00:00'))
		).filter(Events.hostname == host
		).filter(Events.servicename == service)

	   if events.count() == 0 :
		redirect('/dashboard')
	   
	   GenerateTmplContext()

	   events , ids = FormatEvents(events,0,events.count())

	   return dict(
			   events=events,
			   id_first_row=1,
			   id_last_row=1,
			   total_row=1,
			   pages=[1],
			   page=1,
			   event_edit_status_options=edit_event_status_options,
			   history=FormatHistory(ids,host,service),
			   hist_error = True
		)

    def edit_event_form_errors (self,**argv):
	    flash(_(tmpl_context.form_errors),'error')
	    redirect(request.environ.get('HTTP_REFERER').split(request.environ.get('HTTP_HOST'))[1])

    @expose('dashboard.templates.dashboard_update')
    @validate(validators={
	    "id":validators.Regex(r'^[0-9]+(,[0-9]*)*,?$'),
	    "tt":validators.Regex(r'^[0-9]*$'),
	    "status":validators.OneOf(['None', 'Acknowledged', 'AAClosed'])
	    },error_handler=edit_event_form_errors)
    @require(Any(not_anonymous(),msg="You need to be authenticated"))
    def update_event(self,*argv,**krgv):
	   
           ids = krgv['id'].split(',')
	   
	   if len(ids) > 1 :
		   ids = ids[:-1]

	   events = DBSession.query(Events).join(
		( Host, Events.hostname == Host.name ),
		( Service, Events.servicename == Service.name ),
		( HostGroups , Host.name == HostGroups.hostname )
		).filter(HostGroups.groupname.in_(GetUserGroups())
		).filter(Events.idevent.in_(ids))
	   
	   if events.count() <= 0 :
		   flash(_('No access to this event'),'error')
		   redirect('/dashboard')
	   
	   for event in events :
		   if krgv['tt'] != '' :
		   	event.trouble_ticket = krgv['tt']
		   	history = EventHistory(type_action="Ticket change",idevent=event.idevent,value='',text='',username=request.environ.get('repoze.who.identity').get('repoze.who.userid'))
		   	DBSession.add(history)	
	   
		   if events[0].status != krgv['status'] :
		   	event.status = krgv['status']
                   	history = EventHistory(type_action="Acknowlegement change state",idevent=event.idevent,value='',text='',username=request.environ.get('repoze.who.identity').get('repoze.who.userid'))
                   	DBSession.add(history)
	   
   	   flash(_('Updated successfully'))
	   redirect(request.environ.get('HTTP_REFERER').split(request.environ.get('HTTP_HOST'))[1])

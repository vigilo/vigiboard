from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea, CheckBox, Spacer, Label, HiddenField

edit_event_status_options = [['None','Change to None'],['Acknowledged','Change to Acknowledged'],['AAClosed','Change to Closed']]

class Edit_Event_Form(TableForm):

           treatments_options = enumerate((
                'Change to None', 'Change to Acknowledged', 'Change to Closed'))
	   fields = [
		HiddenField('id'),
		#TextArea('comment',label_text='Comment: (Please add your initials)',attrs=dict(rows=5 , cols=25)),
		TextField('tt',label_text='Touble Ticket'),
		#CheckBox('tt_create',label_text='Create'),
		SingleSelectField('status',options=edit_event_status_options),
		Spacer(),Spacer()
		]

	   submit_text='Apply'

class Search_Form(TableForm):

	   fields = [
		TextField('host',label_text='Host'),
		TextField('service',label_text='Service'),
		TextField('output',label_text='Output'),
		TextField('trouble_ticket',label_text='Trouble Ticket'),
		Spacer(),Spacer()
		]

	   submit_text='Search'



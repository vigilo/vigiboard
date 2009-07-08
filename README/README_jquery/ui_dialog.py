# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from tw.api import Widget, CSSLink, js_function
from tw.jquery.direction import jquery_direction_js
from ui_core import jquery_ui_core_js
from ui import ui_dialog_js , ui_draggable_js, ui_resizable_js

__all__ = ["jquery_ui_dialog_js"]

jquery_ui_dialog_css    = CSSLink(modname=__name__,
		filename='static/css/ui.all.css')

jQuery = js_function('jQuery')

class JQueryUIDialog(Widget):
    
    """Generate an instance for an UI Dialog"""

    javascript = [ui_dialog_js, ui_draggable_js, jquery_ui_core_js,
		    jquery_direction_js, ui_resizable_js]
    css = [jquery_ui_dialog_css]
    
    params = ['autoOpen', 'bgiframe', 'buttons', 'closeOnEscape', 'dialogClass'
	'draggable', 'height', 'hide', 'maxHeight', 'maxWidht', 'minHeight', 'minWidth'
	'modal', 'position', 'resizable', 'show', 'stack', 'title', 'width', 'zindex' ]
   
    autoOpen = True
    bgiframe = False
    buttons = {}
    closeOnEscape = True 
    dialogClass = ""
    draggable = True
    height = "auto"
    hide = None
    maxHeight = False
    maxWidth = False
    minHeight = 15
    minWidth = 15
    modal = False
    position = "center"
    resizable = False
    show = None
    stack = True
    title = ''
    width = "auto"
    zindex = 1000

    def update_params(self, d):
        
        """Allow the user to update the UI Dialog parameters"""

        super(JQueryUIDialog, self).update_params(d)
        
        if not getattr(d, "id", None):
            raise ValueError, "JQueryUIDialog is supposed to have id"
    	
        dialog_params = dict (     autoOpen = self.autoOpen,
			bgiframe = self.bgiframe,
			buttons = self.buttons,
			closeOnEscape = self.closeOnEscape,
			dialogClass = self.dialogClass,
			draggable = self.draggable,
			height = self.height,
			hide = self.hide,
			maxHeight = self.maxHeight,
			maxWidth = self.maxWidth,
			minHeight = self.minHeight,
			minWidth = self.minWidth,
			modal = self.modal,
			position = self.position,
			resizable = self.resizable,
			show = self.show,
			stack = self.stack,
			title = self.title,
			width = self.width,
			zindex = self.zindex

			)
        self.add_call(jQuery("#%s" % d.id).dialog(dialog_params))

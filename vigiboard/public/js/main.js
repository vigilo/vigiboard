/*
 * Vigiboard
 *
 * Copyright (C) 2009-2011 CS-SI
 */

var vigiloLog = new Log;
// Activation ou désactivation du log en fonction de valeur de la variable debug.
if (debug_mode) {
    vigiloLog.enableLog();
} else {
    vigiloLog.disableLog();
}


window.search_dialog = null;
window.dlg_open_handler = function () { this.isOpen = true; }
window.dlg_close_handler = function () { this.isOpen = false; }

window.addEvent('domready', function (){
    /**
     * HACK: le closed: True est nécessaire pour éviter que
     * JxLib affiche le panel lors de la création du dialogue
     * (affiche des rectangles blancs). Avec cette modification,
     * le dialogue apparaît replié, mais est considéré comme
     * déplié par Jx.Dialog. Les toggleCollapse permettent de
     * marquer le Dialog comme replié dans Jx.Dialog avant de
     * le déplier pour qu'il soit affiché correctement.
     */
    window.search_dialog = new Jx.Dialog({
        id: "SearchDialog",
        label: _('Search Event'),
        modal: false,
        resize: false,
        move: true,
        content: "search_form",
        onOpen: window.dlg_open_handler,
        onClose: window.dlg_close_handler,
        width: 400,
        height: 325,
        closed: true
    });
    window.search_dialog.toggleCollapse();
    window.search_dialog.toggleCollapse();

    var selector = new TreeGroup({
        url: app_path + '/get_groups',
        app_path: app_path,
        title: _("Select a group")
    });
    $('search_form_supitemgroup').addEvent('click', selector.selectGroup.bind(selector));
    selector.addEvent('select', function (item) {
        $('search_form_supitemgroup.ui').set('value', item.options.label);
        $('search_form_supitemgroup.value').set('value', item.options.data);
    });
    $('search_form_supitemgroup.clear').addEvent('click', function () {
        $('search_form_supitemgroup.ui').set('value', '');
        $('search_form_supitemgroup.value').set('value', '');
    });

    add_autocompleter('search_form_host', 'host', app_path + '/autocomplete/host');
    add_autocompleter('search_form_service', 'service', app_path + '/autocomplete/service');

    change_refresh_rate(refresh_status);

    $$('.date_field_button').addEvent('click', function () {
        $$(".calendar").setStyles({"zIndex": window.search_dialog.domObj.getStyle('zIndex').toInt()});
    });
});

function change_fontsize(size) {
    document.body.style.fontSize = size;
    var req = new Request.JSON({
        link: 'cancel',
        url: app_path + '/set_fontsize',
        onFailure: function () {
            alert(_('Unable to save preferences'));
        }
    });
    req.post({fontsize: size});

    vigiloLog.log("Font size set to " + size + ".");
}

var refresh_timeout = null;
function change_refresh_rate(enabled) {
    var delay = refresh_delay;
    if (refresh_timeout) refresh_timeout = $clear(refresh_timeout);
    if (parseInt(enabled) && delay) refresh_timeout = refresh_page.periodical(delay * 1000);
}

function set_refresh() {
    var enabled = $$('refresh').get('checked') ? 1 : 0;
    var req = new Request.JSON({
        link: 'cancel',
        url: app_path + '/set_refresh',
        onFailure: function () {
            alert(_('Unable to save preferences'));
        }
    });
    req.post({'refresh': enabled});
    change_refresh_rate(enabled);
}

function refresh_page() {
    var dialogs = $$(".jxDialog");
    for (var i=0; i<dialogs.length; i++) {
        if (dialogs[i].getStyle('display') != 'none') {
            vigiloLog.log("A dialog is active on the page ('" + dialogs[i].getElement('.jxDialogLabel').get('text') + "'): refresh is not possible.");
            return;
        }
    }

    vigiloLog.log("No active dialog on the page: refreshing...");
    window.location.reload(true);
}

function change_theme(theme_id, theme_name) {
    var req = new Request.JSON({
        link: 'cancel',
        url: app_path + '/set_theme',
        onFailure: function () {
            alert(_('Unable to save preferences'));
        }
    });
    req.post({'theme': theme_id});
    setActiveStyleSheet(theme_name);

    vigiloLog.log("Theme set to '" + theme_name + "'.");
}

function setActiveStyleSheet(theme_name) {
    $$('link[rel~=stylesheet][title]').each(function (link_obj) {
        link_obj.set('disabled', true);
        if (link_obj.get('title') == theme_name)
            link_obj.set('disabled', false);
    })
}

function add_autocompleter(elem, varname, url) {
    new Autocompleter.Request.VigiloJSON(elem, url, {
        // ATTENTION: domObj n'est pas documenté dans l'API.
        zIndex: window.search_dialog.domObj.getStyle('zIndex').toInt(),
        minLength: 1,
        selectMode: 'pick',
        postVar: varname,
        overflow: true
    });
}


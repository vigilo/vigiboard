/*
 * Vigiboard
 *
 * Copyright (C) 2009-2014 CS-SI
 */

// Fonction d'échappement
function escapeXML(s) {
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/'/g, '&#x27;')
            .replace(/"/g, '&#x22;');
}

/*
 * Classe représentant une boîte de dialogue demandant confirmation à
 * l'utilisateur avant la suppression d'une règle de mise en silence.
 */
var DeleteDialog = new Class({

    // Initialisation de la boîte de dialogue
    initialize: function() {
        var header_height = $("header").getSize().y;
        this.dialog = new Jx.Dialog({
            id: "delete",
            label: 'Delete',
            modal: true,
            width: 370,
            height: 160,
            //horizontal: "right -10",
            //vertical: 'top ' + (header_height + 40),
            resize: true
        });
        this.dialog.addEvent("resize", function() {
            if (this.options.width < 200) {
                this.options.width = 200;
                return this.resize(this.options.width,
                                   this.options.height);
            }
            if (this.options.height < 150) {
                this.options.height = 150;
                return this.resize(this.options.width,
                                   this.options.height);
            }
        });
    },

    // Clôture de la boîte de dialogue
    close: function() {
        this.dialog.close();
    },

    // Affichage de la boîte de dialogue
    show: function(rule_id) {
        var sentence;
        var label;
        var confirmation;
        var objtype;
        var buttonOK;
        var buttonCancel;

        sentence = _("Are you sure you want to delete this rule?");
        label = (_("Silence rule #{id}")).substitute({id: rule_id});
        confirmation = _("Delete this rule");

        sentence = "<p>" + sentence + "</p>";
        this.dialog.setLabel(label);
        this.dialog.setContent(
        "<div class='confirmation_dialog'>" +
            "<div class='confirmation_dialog_question'>" +
                "<img src='/images/warning.png' alt='warning'/>" +
                sentence +
            "</div>" +
            "<div class='confirmation_dialog_buttons'>" +
                "<input id='confirmation_button' class='submit_button'" +
                "  type='submit' value='" + escapeXML(confirmation) + "'/>" +
                "<input id='cancellation_button' class='submit_button'" +
                "  type='submit' value='" + escapeXML(_("No")) + "'/>" +
            "</div>" +
        "</div>"
        );
        confirmation_button = $("confirmation_button");
        confirmation_button.removeEvents("click");
        confirmation_button.addEvent("click", function() {
            new URI("delete?id=" + rule_id).go();
        });

        cancellation_button = $("cancellation_button");
        cancellation_button.removeEvents("click");
        cancellation_button.addEvent("click", function() {
            this.dialog.close();
        }.bind(this));

        this.dialog.open();
    }
});

// Appelé au chargement de la page
window.addEvent('domready', function (){
    var dialog = new DeleteDialog();
    $$(".deletion_link").addEvent(
        "click", function(e) {
            e.stop();
            dialog.show(e.target.getParent().getProperty('href').split('=')[1]);
        }.bind(this)
    );
});

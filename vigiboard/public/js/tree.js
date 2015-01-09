/**
 * VigiBoard, composant de Vigilo.
 * Copyright (C) 2009-2015 CS-SI
 * Licence : GNU GPL v2 ou superieure
 *
 */

/*
 * Affichage en arbre des groupes d'hôtes.
 */
var SelectGroupTree = new Class({
    Implements: [Options, Events],

    options: {
        title: '',
        labelId: null,
        idId: null
    },

    initialize: function(options) {
        this.setOptions(options);

        /* L'objet tree se réfère à un élément div*/
        this.container = new Element('div');
        this.container.setStyle("padding", "0 10px 10px 10px");
        this.tree = new Jx.Tree({parent: this.container});

        this.tree = new GroupTree({
            parent: this.container,
            url: app_path + '/get_groups',
            itemName: "item",
            groupsonly: true,
            onItemClick: this.itemSelected.bind(this),
            onGroupClick: this.itemSelected.bind(this)
        });

        this.dlg = new Jx.Dialog({
            label: this.options.title,
            modal: true,
            resize: true,
            content: this.container
        });
    },

    open: function() {
        this.dlg.open();
    },

    load: function() {
        this.tree.load();
    },

    reload: function() {
        this.tree.clear();
        this.tree.load();
    },

    itemSelected: function(item) {
        if (this.options.labelId !== null) {
            $(this.options.labelId).set('value', item.name);
        }
        if (this.options.idId !== null) {
            $(this.options.idId).set('value', item.id);
        }
        this.dlg.close();
        this.fireEvent("select", [item]);
    }

});

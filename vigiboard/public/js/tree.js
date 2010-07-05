/**
 * VigiBoard, composant de Vigilo.
 * (c) CSSI 2009-2010 <contact@projet-vigilo.org>
 * Licence : GNU GPL v2 ou superieure
 * 
 */

/*
 * Affichage en arbre des groupes.
 */
var TreeGroup = new Class({
    Implements: [Options, Events],

    initialize: function(options) {
        this.setOptions(options);

        /* L'objet tree se réfère à un élément div*/
        var container = new Element('div')
        this.tree = new Jx.Tree({parent: container});

        this.dlg = new Jx.Dialog({
            label: this.options.title,
            modal: true,
            content: container,
        });

        var req = new Request.JSON({
            method: "get",
            url: this.options.url,
            onSuccess: function(groups) {
                $each(groups.groups, function(item) {
                    this.addItem(item, this.tree);
                }, this);
            }.bind(this)
        });
        req.send();
    },

    /* Ajout d'un element à l'arbre */
    addItem: function(data, parent) {
        var subfolder;
        if (data.children.length) {
            subfolder = new Jx.TreeFolder({
                label: data.name,
                data: data.idgroup,
                image: this.options.app_path+"images/map-list.png",
            });
        }
        else {
            subfolder = new Jx.TreeItem({
                label: data.name,
                data: data.idgroup,
                image: this.options.app_path+"images/map.png",
            });
        }

        subfolder.addEvent("click", function() {
            this.fireEvent('select', [subfolder]);
            this.dlg.close();
            return false;
        }.bind(this));
        parent.append(subfolder);

        $each(data.children, function(item) {
            this.addItem(item, subfolder);
        }, this);
    },

    selectGroup: function() {
        this.dlg.open();
    }
});


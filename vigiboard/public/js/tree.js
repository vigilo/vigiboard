/**
 * VigiBoard, composant de Vigilo.
 * (c) CSSI 2009-2010 <contact@projet-vigilo.org>
 * Licence : GNU GPL v2 ou superieure
 *
 */

/*
 * Affichage en arbre des groupes d'hôtes.
 */
var TreeGroup = new Class({
    Implements: [Options, Events],

    initialize: function(options) {
        this.setOptions(options);

        /* L'objet tree se réfère à un élément div*/
        this.container = new Element('div')
        this.container.setStyle("padding", "0 10px 10px 10px");
        this.tree = new Jx.Tree({parent: this.container});

        this.dlg = new Jx.Dialog({
            label: this.options.title,
            modal: true,
            resize: true,
            content: this.container
        });

        this.redraw();
    },

    /* Récupération des items (noeuds/feuilles) de l'arbre dépendant
     * du parent dont l'identifiant est passé en paramètre */
    retrieve_tree_items: function(parent_node, top_node) {

        // Si l'identifiant est bien défini, on ajoute les
        // items  récupérés à leur parent dans l'arbre
        var req = new Request.JSON({
            url: this.options.url,
            onSuccess: function(data, xml) {
                if ($defined(data.groups)) {
                    data.groups.each(function(item) {
                        this.addNode(item, parent_node);
                    }, this);
                }
                if ($defined(data.leaves)) {
                    data.leaves.each(function(item) {
                        this.addLeaf(item, parent_node);
                    }, this);
                }
                this.fireEvent("branchloaded");
            }.bind(this)
        });

        // Envoi de la requête
        if (!$chk(top_node))
            req.get({parent_id: parent_node.options.data});
        else
            req.get();
    },

    /* Ajout d'un noeud à l'arbre */
    addNode: function(data, parent_node) {
        var node = new Jx.TreeFolder({
            label: data.name,
            data: data.id
        });

        node.addEvent("disclosed", function(node) {
            this.fireEvent("nodedisclosed", node);
            if (!node.options.open || node.nodes.length > 0)
                return;
            this.retrieve_tree_items(node);
        }.bind(this));

        node.addEvent("click", function() {
            this[0].fireEvent('select', this[1]);
            this[0].dlg.close();
            return false;
        }.bind([this, node]));

        parent_node.append(node);
    },

    /* Ajout d'une feuille à l'arbre */
    addLeaf: function(data, parent_node) {
        var leaf = new Jx.TreeItem({
            label: data.name,
            data: data.id
        });

        leaf.addEvent("click", function() {
            this.fireEvent('select', [leaf]);
            this.dlg.close();
        }.bind(this));

        parent_node.append(leaf);
    },

    selectGroup: function() {
        this.dlg.open();
    },

    redraw: function() {
        this.tree.clear();
        this.retrieve_tree_items(this.tree, true);
    }
});

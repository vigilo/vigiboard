# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Configuration de Vigiboard."""

vigiboard_config = {
    'vigiboard_bdd.basename' : '',
    
    # Affichage, lien disponibles dans la fenêtre de détail d'un évènement
    'vigiboard_links.eventdetails' : {
        'nagios' : ['Nagios host details','http://example1.com/%(idevent)d'],
        'metrology' : ['Metrology details','http://example2.com/%(idevent)d'],
        'security' : ['Security details','http://example3.com/%(idevent)d'],
        'servicetype' : ['Service Type','http://example4.com/%(idevent)d']
        },
    
    # Nombre d'évènments par pages
    'vigiboard_item_per_page' : '15',
    
    # plugin a activer
    # nom du fichier sans l'extension suivit du nom de la classe
    'vigiboard_plugins' : [
        [ 'shn' , 'PluginSHN' ]
        ],

    # Version de Vigiboard
    'vigiboard_version' : '0.1',

    # URL pour le logo Vigilo, si vide on renvoi sur /
    'vigiboard_links.logo' : '',

    # URL des tickets, possibilités:
    # - %(idevent)d
    # - %(host)s
    # - %(service)s
    # - %(tt)s
    'vigiboard_links.tt' : 'http://example4.com/%(idevent)d/%(tt)s',

    # Taille de police par défaut
    'vigiboard_font.size' : '10'
}


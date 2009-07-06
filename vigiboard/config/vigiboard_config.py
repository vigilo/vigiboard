# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Configuration de Vigiboard."""

vigiboard_config = {
    
    # Affichage, lien disponibles dans la fenêtre de détail d'un évènement
    'vigiboard_links.nagios' : 'http://example1.com/%(idevent)d',
    'vigiboard_links.metrology' : 'http://example2.com/%(idevent)d',
    'vigiboard_links.security' : 'http://example3.com/%(idevent)d',
    'vigiboard_links.servicetype' : 'http://example4.com/%(idevent)d',
    
    # Nombre d'évènments par pages
    'vigiboard_item_per_page' : '15',

    # Nom de base des tables de la base de données
	'vigiboard_bdd.basename' : ''
}


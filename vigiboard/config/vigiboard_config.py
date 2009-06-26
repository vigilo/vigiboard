# -*- coding: utf-8 -*-
"""Configuration for Vigiboard."""

vigiboard_config = {
        'vigiboard_links.nagios' : 'http://example1.com/%(idevent)d',
        'vigiboard_links.metrology' : 'http://example2.com/%(idevent)d',
        'vigiboard_links.security' : 'http://example3.com/%(idevent)d',
        'vigiboard_links.servicetype' : 'http://example4.com/%(idevent)d',
        'vigiboard_item_per_page' : '15',
	'vigiboard_bdd.basename' : ''
}


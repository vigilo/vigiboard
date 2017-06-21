# -*- coding: utf-8 -*-
# Copyright (C) 2006-2016 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Unit and functional test suite for vigiboard."""

from vigilo.turbogears.test import setup_db, teardown_db
from vigilo.turbogears.test import TestController as TestTGController

__all__ = ['setup_db', 'teardown_db', 'TestController']

class TestController(TestTGController):
    def get_rows(self, response):
        return response.lxml.xpath(
            '//table[contains(concat(" ", @class, " "), " vigitable ")]'
            '/tbody/tr')

    def get_cells(self, response):
        return response.lxml.xpath(
            '//table[contains(concat(" ", @class, " "), " vigitable ")]'
            '/tbody/tr/td')

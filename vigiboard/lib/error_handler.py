# vim: set fileencoding=utf-8 sw=4 ts=4 et :
################################################################################
#
# Copyright (C) 2007-2016 CS-SI
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
################################################################################

"""Fonction de gestion des messages d'erreur"""

import logging

from tg import flash, redirect

LOGGER = logging.getLogger(__name__)

def handle_error_message(message, redirection_url='./'):
    """
    Affiche le message dans l'IHM, l'enregistre dans les logs
    et renvoie le navigateur vers l'URL de redirection.

    @param message: message d'erreur à afficher
    @type  message: C{str}
    @param redirection_url: (optionnel) URL de redirection
    @type  redirection_url: C{str}
    """
    LOGGER.error(message)
    flash(message, 'error')
    redirect(redirection_url)

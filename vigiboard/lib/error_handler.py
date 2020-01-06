# vim: set fileencoding=utf-8 sw=4 ts=4 et :
# Copyright (C) 2007-2020 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

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

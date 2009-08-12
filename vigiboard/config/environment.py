# vim: set fileencoding=utf-8 sw=4 ts=4 et :
from __future__ import absolute_import

"""WSGI environment setup for vigiboard."""

from .app_cfg import base_config

__all__ = ['load_environment']

#Use base_config to setup the environment loader function
load_environment = base_config.make_load_environment()

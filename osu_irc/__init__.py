# -*- coding: utf-8 -*-

"""
##################
osu! IRC wrapper
##################

Simple to use IRC connection for osu optimized for the PhaazeOS project
but usable to any purpose

:copyright: (c) 2018-2021 The_CJ
:license: MIT License

- Inspired by the code of Rapptz's Discord library
- Basically a copy of my twitch_irc.py library, just for osu!
"""

__title__ = 'osu_irc'
__author__ = 'The_CJ'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018-2021 The_CJ'
__version__ = "1.2.0"

from .Classes.channel import Channel
from .Classes.client import Client
from .Classes.message import Message
from .Classes.user import User

class Errors(object):
	from .Utils.errors import InvalidAuth, InvalidCredentials, PingTimeout, EmptyPayload

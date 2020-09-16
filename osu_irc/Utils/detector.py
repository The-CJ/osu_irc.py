from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Classes.client import Client

import re
import time
import asyncio
from ..Utils.cmd import sendPong
from ..Utils.errors import InvalidAuth
from ..Utils.handler import (
	handleQuit
)
from ..Utils.regex import (
	ReGarbage, RePing, ReWrongAuth,
	ReOnReady, ReQuit
)

async def garbageDetector(cls:"Client", payload:str) -> bool:
	"""
	This detector is suppost to catch all known patterns that are also known as trash.
	Like this the very beginning where bancho boat is drawn in ASCII
	"""
	if re.match(ReGarbage, payload) != None:
		return True

	return False

async def mainEventDetector(cls:"Client", payload:str) -> bool:
	"""
	This detector is suppost to catch all events we can somehow process, if not, give back False.
	If that happens the Client `cls` makes additional handling
	"""

	#response to PING
	if re.match(RePing, payload) != None:
		cls.last_ping = time.time()
		await sendPong(cls)
		return True

	# handels events: onQuit
	if re.match(ReQuit, payload) != None:
		return await handleQuit(cls, payload)

	# handels events: onReady, onReconnect
	if re.match(ReOnReady, payload) != None:
		if cls.auth_success:
			#means we got a reconnect
			asyncio.ensure_future( cls.onReconnect() )
		cls.auth_success = True
		asyncio.ensure_future( cls.onReady() )
		return True

	# wrong_auth
	if not cls.auth_success:
		if re.match(ReWrongAuth, payload) != None:
			raise InvalidAuth( payload )

	return False

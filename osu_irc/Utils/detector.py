from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Classes.client import Client

import re
import time
import asyncio
from ..Utils.cmd import sendPong
from ..Utils.errors import InvalidAuth
from ..Utils.handler import (
	handleJoin, handlePart, handleQuit,
	handleUserList, handlePrivMessage, handleMOTDEvent,
	handleMode
)
from ..Utils.regex import (
	ReGarbage, RePing, ReWrongAuth,
	ReOnReady, ReUserList, RePrivMessage,
	ReJoin, RePart, ReQuit,
	ReMOTD, ReMode
)

async def garbageDetector(_cls:"Client", payload:str) -> bool:
	"""
	This detector is suppose to catch all known patterns that are also known as trash.
	Like this the very beginning where bancho boat is drawn in ASCII
	"""
	if re.match(ReGarbage, payload) is not None:
		return True

	return False

async def mainEventDetector(cls:"Client", payload:str) -> bool:
	"""
	This detector is suppose to catch all events we can somehow process, if not, give back False.
	If that happens the Client `cls` makes additional handling
	"""

	# response to PING
	if re.match(RePing, payload) is not None:
		cls.last_ping = time.time()
		await sendPong(cls)
		return True

	# handles events: onJoin
	if re.match(ReJoin, payload) is not None:
		return await handleJoin(cls, payload)

	# handles events: onPart
	if re.match(RePart, payload) is not None:
		return await handlePart(cls, payload)

	# handles events: onQuit
	if re.match(ReQuit, payload) is not None:
		return await handleQuit(cls, payload)

	# handles events: onMessage
	if re.match(RePrivMessage, payload) is not None:
		return await handlePrivMessage(cls, payload)

	# handles events: None
	if re.match(ReUserList, payload) is not None:
		return await handleUserList(cls, payload)

	# handles events: None
	if re.match(ReMOTD, payload) is not None:
		return await handleMOTDEvent(cls, payload)

	# handles events: None
	if re.match(ReMode, payload) is not None:
		return await handleMode(cls, payload)

	# handles events: onReady, onReconnect
	if re.match(ReOnReady, payload) is not None:
		if cls.auth_success:
			# means we got a reconnect
			asyncio.ensure_future(cls.onReconnect())
		cls.auth_success = True
		asyncio.ensure_future(cls.onReady())
		return True

	# wrong_auth
	if not cls.auth_success:
		if re.match(ReWrongAuth, payload) is not None:
			raise InvalidAuth(payload)

	return False

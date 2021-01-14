from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Classes.client import Client

import asyncio

async def addTraffic(cls:"Client"):
	"""
	should be called after every write counting action (PRIVMSG, JOIN, MSG...)
	Increases traffic value for 30 sec
	"""
	cls.traffic += 1
	await asyncio.sleep(30)
	cls.traffic -= 1

async def trafficQuery(cls:"Client"):
	"""
	get started on Client.start(),
	a coro that's takes all requests that would be over the limit
	and send them later
	"""
	while cls.running and cls.query_running:
		if cls.traffic <= (cls.request_limit-1) and len(cls.stored_traffic) > 0:
			req = cls.stored_traffic.pop(0)
			await cls.sendContent(req)
		else:
			await asyncio.sleep(0.05)

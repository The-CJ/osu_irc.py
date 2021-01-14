from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Classes.client import Client

async def sendPong(cls:"Client"):
	await cls.sendContent("PONG :cho.ppy.sh\r\n", ignore_limit=True)

async def sendNick(cls:"Client"):
	await cls.sendContent(f"NICK {cls.nickname}\r\n", ignore_limit=True)

async def sendPass(cls:"Client"):
	await cls.sendContent(f"PASS {cls.token}\r\n", ignore_limit=True)

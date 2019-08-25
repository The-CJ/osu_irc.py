from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

async def sendMessage(cls:"Client", channel:str, message:str):
	channel = channel.lower().strip('#')
	await cls.sendContent( f"PRIVMSG #{channel} :{message}\r\n" )

async def sendPM(cls:"Client", user:str, message:str):
	user = user.lower().strip('#')
	await cls.sendContent( f"PRIVMSG {user} :{message}\r\n" )

async def joinChannel(cls:"Client", channel:str):
	channel = channel.lower().strip('#')
	await cls.sendContent( f"JOIN #{channel}\r\n" )

async def partChannel(cls:"Client", channel:str):
	channel = channel.lower().strip('#')
	await cls.sendContent( f"PART #{channel}\r\n" )


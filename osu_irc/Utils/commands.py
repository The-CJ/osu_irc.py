from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

from ..Classes.channel import Channel
from ..Classes.user import User

import logging
Log:logging.Logger = logging.getLogger("osu_irc")

async def sendMessage(cls:"Client", Chan:Channel or str, content:str):
	"""
	This will send the content/message to a channel. (If you are not timed out, banned or otherwise, that not my fault duh)
	1st arg, `Chan` is the destination, provide a `Channel` object or a string like "osu", where you want to send your 2nd arg `content`.

	All IRC Channel-names start with a '#' you don't have to provide this, we will handle everything. ("#osu" == "osu")
	For sending messages to a User (PM) use sendPM()
	"""
	if isinstance(Chan, Channel):
		destination:str = Chan.name
	elif isinstance(Chan, User):
		raise ValueError(f"sendMessage() is meant for channels only, please use sendPM() for messages to a user")
	else:
		destination:str = str(Chan)

	destination = destination.lower().strip('#').strip(' ')
	Log.debug(f"Sending: PRIVMSG #{destination} - {content[:50]}")
	await cls.sendContent( f"PRIVMSG #{destination} :{content}\r\n" )

async def sendPM(cls:"Client", Us:User or str, content:str):
	"""
	This will send the content/message to a user. (If you are not blocked or otherwise)
	1st arg, `Us` is the destination, provide a `User` object or a string like "The_CJ", where you want to send your 2nd arg `content`.

	For sending messages to a channel use sendMessage()
	"""
	if isinstance(Us, User):
		destination:str = Us.name
	elif isinstance(Us, Channel):
		raise ValueError(f"sendPM() is meant for users only, please use sendMessage() for messages to a channel")
	else:
		destination:str = str(Us)

	destination = destination.lower().strip('#').strip(' ')
	Log.debug(f"Sending: PRIVMSG {destination} - {content[:50]}")
	await cls.sendContent( f"PRIVMSG {destination} :{content}\r\n" )

async def joinChannel(cls:"Client", Chan:Channel or str):
	"""
	Joining a channel allows the client to receive messages from this channel.
	`Chan` is the destination, provide a `Channel` object or a string like "osu" or "#lobby"

	All IRC Channel-names start with a '#' you don't have to provide this, we will handle everything. ("#osu" == "osu")
	"""
	if isinstance(Chan, Channel):
		destination:str = Chan.name
	elif isinstance(Chan, User):
		raise ValueError(f"you can not join a user, just start PM-ing, duh")
	else:
		destination:str = str(Chan)

	destination = destination.lower().strip('#')
	Log.debug(f"Sending: JOIN #{destination}")
	await cls.sendContent( f"JOIN #{destination}\r\n" )

async def partChannel(cls:"Client", Chan:Channel or str):
	"""
	Parting a channel disables receiving messages from this channel.
	`Chan` may is a `Channel` object or a string like "osu" or "#lobby"

	All IRC Channel-names start with a '#' you don't have to provide this, we will handle everything. ("#osu" == "osu")
	"""
	if isinstance(Chan, Channel):
		destination:str = Chan.name
	elif isinstance(Chan, User):
		raise ValueError(f"you can not part a user, its not a channel, duh")
	else:
		destination:str = str(Chan)

	destination = destination.lower().strip('#')
	Log.debug(f"Sending: PART #{destination}")
	await cls.sendContent( f"PART #{destination}\r\n" )

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

import asyncio
from ..Classes.message import Message
# from .message import Message

async def handleOnMessage(cls:"Client", payload:str):
	"""
	handles all messages and calls
	self.onMessage(Message) for custom user code
	"""

	# generate message
	Msg = Message(payload)

	asyncio.ensure_future( cls.onMessage( Msg ) )


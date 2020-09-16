from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

import asyncio
# from ..Classes.message import Message
# from .message import Message

import logging
Log:logging.Logger = logging.getLogger("osu_irc")

async def handleQuit(cls:"Client", payload:str) -> bool:
	"""
	handles all QUIT events

	may calls the following events for custom code:
	- onMemberQuit(User)

	"""
	return True

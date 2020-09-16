from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

# from ..Classes.message import Message
# from .message import Message

import logging
Log:logging.Logger = logging.getLogger("osu_irc")

import re
from ..Classes.channel import Channel
from ..Classes.user import User

from ..Utils.regex import ReUserListData

async def handleJoin(cls:"Client", payload:str) -> bool:
	"""
	handles all JOIN events

	may calls the following events for custom code:
	- onMemberJoin(Channel, User)
	"""
	return True

async def handlePart(cls:"Client", payload:str) -> bool:
	"""
	handles all PART events

	may calls the following events for custom code:
	- onMemberPart(Channel, User)
	"""
	return True

async def handleQuit(cls:"Client", payload:str) -> bool:
	"""
	handles all QUIT events, an ooo boi ate there a lot of them

	may calls the following events for custom code:
	- onMemberQuit(User)
	"""
	return True

async def handleUserList(cls:"Client", payload:str) -> bool:
	"""
	User-List aka, IRC Event: 353
	which means a list of all users that already are in the channel when the Client joined.

	may calls the following events for custom code:
	- None
	"""

	# e.g.: :cho.ppy.sh 353 Phaazebot = #osu :The_CJ Someone +SomeoneViaIRC
	return True
	search:re.Match = re.search(ReUserListData, payload)
	if search != None:
		room_name:str = search.group(1)
		ChannelToFill:Channel = cls.channels.get(room_name, None)
		if not ChannelToFill: return True

		full_user_list:str = search.group(2)
		for user_name in full_user_list.split(' '):

			if user_name.lower() == cls.nickname.lower(): continue

			KnownUser:User = cls.users.get(user_name, None)
			if not KnownUser:
				KnownUser:User = User(None)
				KnownUser._name = user_name
				KnownUser.minimalistic = True

				cls.users[KnownUser.name] = KnownUser

			Log.debug(f"New Entry to `already-known-user-list`: {ChannelToFill.name} - {KnownUser.name}")
			ChannelToFill.viewers[KnownUser.name] = KnownUser
			KnownUser.found_in.add(ChannelToFill.name)

	return True

async def handlePrivMessage(cls:"Client", payload:str) -> bool:
	"""
	handles all PRIVMSG events

	may calls the following events for custom code:
	- onMessage(Message)
	"""
	return True

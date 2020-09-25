from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User as OsuUser
    from .channel import Channel as OsuChannel

import re
from .undefined import UNDEFINED
from ..Utils.regex import (
	ReUserName,
	ReRoomName,
	ReContent,
	ReAction
)

from ..Utils.commands import sendMessage, sendPM

class Message(object):
	"""
	This class represents a message.
	to see if this message was send via PM or in a channel look at `bool` .is_private
	This class is generated when a user is sending a message, it turns raw data like:

	```
	Channel:
	:The_CJ!cho@ppy.sh PRIVMSG #osu :reeeeee

	PM:
	:The_CJ!cho@ppy.sh PRIVMSG Phaazebot :hello there
	```
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.channel_name}' user='{self.user_name}'>"

	def __str__(self):
		return self.content

	def __init__(self, raw:str or None):
		# props
		self._user_name:str = UNDEFINED
		self._room_name:str = UNDEFINED
		self._content:str = UNDEFINED

		# classes
		self.Author:"OsuUser" = None
		self.Channel:"OsuChannel" = None

		# other
		self.is_action:bool = False
		self._channel_type:int = 0

		if raw != None:
			try:
				self.messageBuild(raw)

			except:
				raise AttributeError(raw)

	# utils
	def compact(self) -> dict:
		d:dict = {}
		d["user_name"] = self.user_name
		d["room_name"] = self.room_name
		d["content"] = self.content
		d["is_action"] = self.is_action
		d["is_private"] = self.is_private
		d["channel_type"] = self.channel_type
		return d

	def messageBuild(self, raw:str) -> None:
		search:re.Match

		# _user_name
		search = re.search(ReUserName, raw)
		if search != None:
			self._user_name = search.group(1)

		# _room_name
		search = re.search(ReRoomName, raw)
		if search != None:
			self._room_name = search.group(1)

		# _content
		search = re.search(ReContent, raw)
		if search != None:
			self._content = search.group(1)

		self.checkType()
		self.checkAction()

	def checkType(self) -> None:
		"""
		Just looks if the name starts with a #, if yes, than the message comes from a room,
		any we remove the #, to keep all names clean
		"""
		if self.room_name.startswith('#'):
			self._room_name = self.room_name.strip('#')
			self._channel_type = 1
		else:
			self._channel_type = 2

	def checkAction(self) -> None:
		"""
		Checks if the message is a action,
		action means its a /me message. If it is, change content and set is_action true
		"""
		search:re.Match = re.search(ReAction, self.content)
		if search != None:
			self.is_action = True
			self._content = search.group(1)

	# need to give ctx for this to work
	def reply(self, ctx, reply:str = 'No Response'):
		if self._channel_type == 1: return sendMessage(ctx, self._room_name, reply)
		if self._channel_type == 2: return sendPM(ctx, self._user_name, reply)

	# props
	@property
	def user_name(self) -> str:
		return str(self._user_name or "")

	@property
	def room_name(self) -> str:
		return str(self._room_name or "")

	@property
	def content(self) -> str:
		return str(self._content or "")

	@property
	def channel_type(self) -> str:
		if self._channel_type == 0: return "Unset"
		if self._channel_type == 1: return "Room"
		if self._channel_type == 2: return "PM"
		else: return "Unknown"

	@property
	def is_private(self) -> bool:
		return bool(self._channel_type == 2)

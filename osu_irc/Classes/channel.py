from typing import Dict, NewType
UserName = NewType("UserName", str)

from .user import User
from .stores import UserStore
from .undefined import UNDEFINED

class Channel(object):
	"""
	This class represents a osu! irc-channel.
	It is generated when the bot join's a chat room.
	Other than twitch, there are not a billion different states a channel can be in,
	so its just a name and user storage i guess.
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} name='{self.name}'>"

	def __str__(self):
		return self.name or ""

	def __init__(self, raw:str or None):

		self._name:str = UNDEFINED
		self._chatters:Dict[UserName, User] = UserStore()

		if raw != None:
			try:
				self.channelBuild(raw)
			except:
				raise AttributeError(raw)

	def compact(self) -> dict:
		d:dict = {}
		d["name"] = self.name
		d["chatter"] = self.chatter
		return d

	# utils
	def channelBuild(self, raw:str) -> None:
		"""
		generated hey we (the client user) joins a channel
		"""

	@property
	def chatters(self) -> Dict[UserName, User]:
		return self._chatters
	@property
	def users(self) -> Dict[UserName, User]:
		return self.chatters

	@property
	def name(self) -> str:
		return str(self._name or "")

from typing import Dict, NewType, Set
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

	def __init__(self, *x, **xx):

		self._name:str = UNDEFINED
		self._chatters:Dict[UserName, User] = UserStore()

		# because of user stores, we save the name of the different user types in a channel
		self._owner:Set[str] = set() # ~
		self._admin:Set[str] = set() # @
		self._operator:Set[str] = set() # &
		self._helper:Set[str] = set() # %
		self._voiced:Set[str] = set() # +

		# other than twitch, this class dosn't has a build function,
		# because it should only be created by a handler (probl. mostly handleJoin)

	def compact(self) -> dict:
		d:dict = {}
		d["name"] = self.name
		d["chatter"] = self.chatter
		return d

	# props
	@property
	def chatters(self) -> Dict[UserName, User]:
		return self._chatters
	@property
	def users(self) -> Dict[UserName, User]:
		return self.chatters

	@property
	def name(self) -> str:
		return str(self._name or "")

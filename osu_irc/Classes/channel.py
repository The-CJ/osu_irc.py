from typing import Dict, NewType, Set, List, TYPE_CHECKING, Union, Optional
if TYPE_CHECKING:
	from .client import Client as OsuClient

from .user import User
from .stores import UserStore

UserName = NewType("UserName", str)

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

	def __init__(self, *_, **__):

		# props
		self._name:Optional[str] = None
		self._chatters:Dict[Union[UserName, str], User] = UserStore()

		# other
		self.motd:str = ""

		# because of user stores, we save the name of the different user types in a channel
		# Update: so... em, yeah, in osu there are no IRC- Owner (~), Operator (&) or Helper (%)
		# the Owner would be BanchBot, i guess, but technically these 3 could be taken out, but i don't give a fuck. REEEEEE
		self._owner:Set[str] = set() # ~
		self._admin:Set[str] = set() # @
		self._operator:Set[str] = set() # &
		self._helper:Set[str] = set() # %
		self._voiced:Set[str] = set() # +

		# other than twitch, this class doesn't has a build function,
		# because it should only be created by a handler (probably. mostly handleJoin)

	def compact(self) -> dict:
		d:dict = dict()
		d["name"] = self.name
		d["motd"] = self.motd
		d["chatters"] = self.chatters
		return d

	# utils
	def getViewer(self, **search:dict) -> User or None:
		"""
		get a user from the channel chatters based on the given kwargs,
		returns the first user all kwargs are valid, or None if 0 valid
		"""

		for user_name in self.users:
			Chatter:User = self.users[user_name]

			valid:bool = True

			for key in search:
				if getattr(Chatter, key, object) != search[key]:
					valid = False
					break

			if valid: return Chatter

		return None

	def getOwners(self) -> List[User]:
		"""
		get all users that are owner (~) of the current channel.
		(NOTE: i never find any in the result... but maybe there are owner... i mean BanchoBot Should be one, right?)
		"""

		owners:List[User] = []

		for owner_name in self._owner:
			U:User = self.users.get(owner_name, None)
			if not U: continue
			owners.append(U)

		return owners

	def getAdmins(self) -> List[User]:
		"""
		get all users that are admins (@) of the current channel.
		(NOTE: same as owner... i never saw any, but hey)
		"""

		admins:List[User] = []

		for admin_name in self._admin:
			U:User = self.users.get(admin_name, None)
			if not U: continue
			admins.append(U)

		return admins

	def getOperators(self) -> List[User]:
		"""
		get all users that are operator (@) of the current channel.
		"""

		operator:List[User] = []

		for operator_name in self._operator:
			U:User = self.users.get(operator_name, None)
			if not U: continue
			operator.append(U)

		return operator

	def getHelpers(self) -> List[User]:
		"""
		get all users that are helper (%) of the current channel.
		"""

		helper:List[User] = []

		for helper_name in self._helper:
			U:User = self.users.get(helper_name, None)
			if not U: continue
			helper.append(U)

		return helper

	def getVoiced(self) -> List[User]:
		"""
		get all users that are voiced (+) of the current channel.
		which in osu!'s case means, "who is connected via an IRC Client and not via game"
		[Random fact, u... i mean, that client here will have a +]
		"""

		voiced:List[User] = []

		for voiced_name in self._voiced:
			U:User = self.users.get(voiced_name, None)
			if not U: continue
			voiced.append(U)

		return voiced

	# funcs
	async def sendMessage(self, cls:"OsuClient", content:str) -> None:
		"""
		Send a message to the channel,
		requires you to give this function the Client class, don't ask why...

		this is basically an alternative to:
		cls.sendMessage(Channel.name, content)

		makes you think... is this even faster? i dunno, adding it anyways LULW
		"""
		return await cls.sendMessage(self.name, content)

	# props
	@property
	def chatters(self) -> Dict[Union[UserName, str], User]:
		return self._chatters

	@property
	def users(self) -> Dict[Union[UserName, str], User]:
		return self.chatters

	@property
	def name(self) -> str:
		return str(self._name or "")

from typing import List, Dict, NewType, Optional, Union
import logging

import time
import asyncio
import traceback
from .message import Message
from .stores import ChannelStore, UserStore
from .channel import Channel
from .user import User
from ..Utils.cmd import sendNick, sendPass
from ..Utils.errors import InvalidAuth, PingTimeout, EmptyPayload, InvalidCredentials
from ..Utils.traffic import addTraffic, trafficQuery
from ..Utils.detector import mainEventDetector, garbageDetector

Log:logging.Logger = logging.getLogger("osu_irc")
ChannelName = NewType("ChannelName", str)
UserName = NewType("UserName", str)


class Client(object):
	"""
	Main class for everything.
	Init and call .run()

	Optional Keyword Arguments
	--------------------------
	* `Loop` - asyncio.AbstractEventLoop  : (Default: asyncio.get_event_loop()) [Main event loop, used for everything]
	* `reconnect` - bool : (Default: True) [Should the client automatically try to reconnect]
	* `nickname` - str` : (Default: None) [User nickname, only lowercase]
	* `token` str : (Default: None) [User oauth token]
	* `request_limit` int : (Default: 15)[ How many requests can be send before the client goes into rate limit protection (request_limit per 60 sec)]
	"""
	def __init__(self, Loop:Optional[asyncio.AbstractEventLoop]=None, **kwargs):

		# vars
		self.Loop:asyncio.AbstractEventLoop = asyncio.get_event_loop() if Loop is None else Loop
		self.reconnect:bool = kwargs.get("reconnect", True)
		self.nickname:str = kwargs.get("nickname", None)
		self.token:str = kwargs.get("token", None)
		self.request_limit:int = kwargs.get("request_limit", 15)

		# static* vars
		self.host:str = "irc.ppy.sh"
		self.port:int = 6667

		# runtime vars
		self.running:bool = False
		self.auth_success:bool = False
		self.query_running:bool = False
		self.last_ping:float = time.time()
		self.traffic:int = 0
		self.stored_traffic:List[str, bytes] = []

		# Connection objects
		self.ConnectionReader:Optional[asyncio.StreamReader] = None
		self.ConnectionWriter:Optional[asyncio.StreamWriter] = None

		self.channels:Dict[Union[ChannelName, str], Channel] = ChannelStore()
		self.users:Dict[Union[UserName, str], User] = UserStore()

	def stop(self, *_, **__) -> None:
		"""
		gracefully shuts down the bot, .start and .run will be no longer blocking
		"""
		Log.debug(f"Client.stop() has been called, shutting down")
		self.running = False
		self.ConnectionWriter.close()
		self.Loop.stop()

	def run(self) -> None:
		"""
		Blocking call that starts the bot, it will wrap .start() into a coroutine for you.

		### This function is blocking, it only returns after .stop() is called
		"""

		if self.running:
			raise RuntimeError("already running")

		Log.debug(f"Client.run() has been called, creating loop and wrapping future")
		MainFuture:asyncio.Future = asyncio.ensure_future(self.start(), loop=self.Loop)
		MainFuture.add_done_callback(self.stop)
		try:
			Log.debug(f"Client.run() starting Client.start() future")
			self.Loop.run_forever()
		except KeyboardInterrupt:
			Log.debug(f"Client.run() stopped by KeyboardInterrupt")
		finally:
			# everything where should be run after Client.stop() or when something breaks the Client.Loop

			# Client.stop should be called once, if you break out via exceptions,
			# since Client.stop also called the Loop to stop, we do some cleanup now
			MainFuture.remove_done_callback(self.stop)
			Log.debug(f"Removing MainFuture callback")

			# gather all task of the loop (that will mostly be stuff like: addTraffic())
			Log.debug(f"Collecting all Client.Loop tasks")
			tasks:List[asyncio.Task] = [task for task in asyncio.Task.all_tasks(self.Loop) if not task.done()]
			Log.debug(f"Canceling {len(tasks)} tasks...")
			for task in tasks:
				task.cancel() # set all task to be cancelled

			Log.debug(f"Cancelled all tasks")

			# and now start the loop again, which will result that all tasks are instantly finished and done
			Log.debug(f"Restarting loop to discard tasks")
			self.Loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

			# then close it... and i dunno, get a coffee or so
			Log.debug(f"All task discarded, closing loop")
			self.Loop.close()

	async def start(self) -> None:
		"""
		Blocking call that starts the bot, this function is a coroutine.

		### This function is blocking, it only returns after .stop() is called

		## Warning!
		This function should be ideally handled via .run()
		because else, there will be no cleanup of futures and task on .stop()
		Which actually is totally ok, but its messy and not really intended.
		If you don't add loop cleanup yourself,
		your console will be flooded by `addTraffic` coroutines waiting to be completed.
		"""
		if self.running:
			raise RuntimeError("already running")

		self.running = True
		self.query_running = True

		if self.token is None or self.nickname is None:
			raise AttributeError("'token' and 'nickname' must be provided")

		Log.debug(f"Client.start() all required fields found, awaiting Client.main()")
		await self.main()

	async def main(self) -> None:
		"""
		a loop that creates the connections and processes all events
		if self.reconnect is active, it handles critical errors with a restart of the bot
		will run forever until self.stop() is called
		or a critical error without reconnect
		"""
		while self.running:

			# reset bot storage
			self.last_ping = time.time()
			self.traffic = 0
			self.channels = ChannelStore()
			self.users = UserStore()
			self.query_running = True
			self.auth_success = False
			if self.ConnectionWriter:
				self.ConnectionWriter.close()

			# not resetting self.stored_traffic, maybe there is something inside
			Log.debug("Client resettled main attributes")

			try:
				# init connection
				self.ConnectionReader, self.ConnectionWriter = await asyncio.open_connection(host=self.host, port=self.port)
				Log.debug("Client successful create connection Reader/Writer pair")

				# login
				await sendPass(self)
				await sendNick(self)

				# start listen
				asyncio.ensure_future(trafficQuery(self))
				Log.debug("Client sent base data, continue to listen for response...")
				await self.listen() # <- that processes stuff

			except InvalidAuth:
				Log.error("Invalid Auth for osu!, please check `token` and `nickname`, not trying to reconnect")
				self.stop()
				continue

			except InvalidCredentials:
				Log.error("osu! never send any response, check credentials for syntax, not trying to reconnect")
				self.stop()
				continue

			except EmptyPayload as E:
				Log.error("Empty payload from osu, trying reconnect")
				await self.onError(E)
				continue

			except PingTimeout as E:
				Log.error("osu! don't give ping response, trying reconnect")
				await self.onError(E)
				continue

			except KeyboardInterrupt:
				self.stop()
				continue

			except Exception as E:
				await self.onError(E)
				if self.running:
					await asyncio.sleep(5)
				else:
					continue

	async def listen(self):

		# listen to osu
		while self.running:

			Log.debug("Client awaiting response...")
			payload:bytes = await self.ConnectionReader.readline()
			Log.debug(f"Client received {len(payload)} bytes of data.")
			asyncio.ensure_future(self.onRaw(payload))
			payload:str = payload.decode('UTF-8').strip('\n').strip('\r')

			# just to be sure
			if payload in ["", " ", None] or not payload:
				if self.auth_success:
					raise EmptyPayload()
				else:
					raise InvalidCredentials()

			# last ping is over 6min (way over twitch normal response)
			if (time.time() - self.last_ping) > 60*6:
				raise PingTimeout()

			# check if the content is known garbage
			garbage:bool = await garbageDetector(self, payload)
			if garbage:
				Log.debug("Client got garbage response, launching: Client.onGarbage")
				asyncio.ensure_future(self.onGarbage(payload))
				continue

			# check if there is something usefully we know
			processed:bool = await mainEventDetector(self, payload)
			if not processed:
				Log.debug("Client got unknown response, launching: Client.onUnknown")
				asyncio.ensure_future(self.onUnknown(payload))
				continue

	async def sendContent(self, content:bytes or str, ignore_limit:bool=False) -> None:
		"""
		used to send content of any type to osu
		pretty much all content should be sent via a other function like, sendMessage, sendPM or whatever
		else that chance that the server understands what you want is near 0
		"""
		if type(content) != bytes:
			content = bytes(content, 'UTF-8')

		if (self.traffic <= self.request_limit) or ignore_limit:
			asyncio.ensure_future(addTraffic(self))
			asyncio.ensure_future(self.onSend(content))
			Log.debug(f"Client sending {len(content)} bytes of content to the ConnectionWriter")
			self.ConnectionWriter.write(content)

		else:
			asyncio.ensure_future(self.onLimit(content))
			self.stored_traffic.append(content)

	# commands
	async def sendMessage(self, Chan:Union[Channel, str], content: str):
		"""
		This will send the content/message to a channel. (If you are not timed out, banned or otherwise, that not my fault duh)
		1st arg, `Chan` is the destination, provide a `Channel` object or a string like "osu", where you want to send your 2nd arg `content`.

		All IRC Channel-names start with a '#' you don't have to provide this, we will handle everything. ("#osu" == "osu")
		For sending messages to a User (PM) use sendPM()
		"""
		if not content:
			raise AttributeError("Can't send empty content")

		if isinstance(Chan, Channel):
			destination: str = Chan.name
		elif isinstance(Chan, User):
			raise ValueError(f"sendMessage() is meant for channels only, please use sendPM() for messages to a user")
		else:
			destination: str = str(Chan)

		destination = destination.lower().strip('#').strip(' ')
		Log.debug(f"Sending: PRIVMSG #{destination} - {content[:50]}")
		await self.sendContent(f"PRIVMSG #{destination} :{content}\r\n")

	async def sendPM(self, Us:Union[User, str], content: str):
		"""
		This will send the content/message to a user. (If you are not blocked or otherwise)
		1st arg, `Us` is the destination, provide a `User` object or a string like "The_CJ", where you want to send your 2nd arg `content`.

		For sending messages to a channel use sendMessage()
		"""
		if not content:
			raise AttributeError("Can't send empty content")

		if isinstance(Us, User):
			destination: str = Us.name
		elif isinstance(Us, Channel):
			raise ValueError(f"sendPM() is meant for users only, please use sendMessage() for messages to a channel")
		else:
			destination: str = str(Us)

		destination = destination.lower().strip('#').strip(' ')
		Log.debug(f"Sending: PRIVMSG {destination} - {content[:50]}")
		await self.sendContent(f"PRIVMSG {destination} :{content}\r\n")

	async def joinChannel(self, Chan:Union[Channel, str]):
		"""
		Joining a channel allows the client to receive messages from this channel.
		`Chan` is the destination, provide a `Channel` object or a string like "osu" or "#lobby"

		All IRC Channel-names start with a '#' you don't have to provide this, we will handle everything. ("#osu" == "osu")
		"""
		if isinstance(Chan, Channel):
			destination: str = Chan.name
		elif isinstance(Chan, User):
			raise ValueError(f"you can not join a user, just start PM-ing, duh")
		else:
			destination: str = str(Chan)

		destination = destination.lower().strip('#')
		Log.debug(f"Sending: JOIN #{destination}")
		await self.sendContent(f"JOIN #{destination}\r\n")

	async def partChannel(self, Chan:Union[Channel, str]):
		"""
		Parting a channel disables receiving messages from this channel.
		`Chan` may is a `Channel` object or a string like "osu" or "#lobby"

		All IRC Channel-names start with a '#' you don't have to provide this, we will handle everything. ("#osu" == "osu")
		"""
		if isinstance(Chan, Channel):
			destination: str = Chan.name
		elif isinstance(Chan, User):
			raise ValueError(f"you can not part a user, its not a channel, duh")
		else:
			destination: str = str(Chan)

		destination = destination.lower().strip('#')
		Log.debug(f"Sending: PART #{destination}")
		await self.sendContent(f"PART #{destination}\r\n")

	# events
	# noinspection PyMethodMayBeStatic
	async def onError(self, Ex:BaseException) -> None:
		"""
		called every time something goes wrong
		"""
		Log.error(Ex)
		traceback.print_exc()

	async def onLimit(self, payload:bytes) -> None:
		"""
		called every time a request was not send because it hit the limit,
		the request is stored and send as soon as possible
		"""
		pass

	async def onRaw(self, raw:bytes) -> None:
		"""
		called every time some bytes of data get received by the client
		"""
		pass

	async def onSend(self, raw:bytes) -> None:
		"""
		called every time some bytes of data get send by the client
		"""
		pass

	async def onReady(self) -> None:
		"""
		called when the client is connected to bancho and is ready to receive or send data
		"""
		pass

	async def onReconnect(self) -> None:
		"""
		called when the client was already connected but was/had to reconnect
		if already connected a onReconnect and onReady fire at the same time
		"""
		pass

	async def onMessage(self, Msg:"Message") -> None:
		"""
		called when the client received a message
		should have a .Channel and .Author class have attached to it
		PM have .is_private == True

		Also: if Msg.is_private then Msg.room_name.lower() == self.nickname.lower()
		[that what a private message is... duh]
		"""
		pass

	async def onMemberJoin(self, Chan:Channel, Us:User) -> None:
		"""
		called when a user joined a osu! channel
		"""
		pass

	async def onMemberPart(self, Chan:Channel, Us:User) -> None:
		"""
		called when a user parts a osu! channel
		"""
		pass

	async def onMemberQuit(self, Us:User, reason:str) -> None:
		"""
		called when a user quits the osu! irc server
		"""
		pass

	async def onGarbage(self, raw:str) -> None:
		"""
		called every time some bytes of data are known garbage that is no useful event
		"""
		pass

	async def onUnknown(self, raw:str) -> None:
		"""
		called every time some bytes of data could not be processed to another event
		"""
		pass

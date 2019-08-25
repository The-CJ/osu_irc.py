import time
import asyncio
import traceback
import re
from ..Utils.cmd import sendNick, sendPass, sendPong
from ..Utils.errors import InvalidAuth, PingTimeout, EmptyPayload
from ..Utils.traffic import addTraffic, trafficQuery
from ..Utils.handler import (
	handleOnMessage
)
from ..Utils.regex import (
	RePing, ReOnReady, ReOnMessage, ReWrongAuth
)
class Client():
	"""
		Main class for everything.
		Init and call .run()
	"""
	def __init__(self, token:str=None, nickname:str=None, reconnect:bool=True, request_limit:int=15):

		self.running:bool = False
		self.auth_success:bool = False
		self.query_running:bool = False
		self.reconnect:bool = reconnect

		self.token:str = token
		self.nickname:str = nickname
		self.host:str = "irc.ppy.sh"
		self.port:int = 6667
		self.last_ping:int = time.time()

		self.ConnectionReader:asyncio.StreamReader = None
		self.ConnectionWriter:asyncio.StreamWriter = None

		self.request_limit:int = request_limit
		self.traffic:int = 0
		self.stored_traffic:list = list()

	def stop(self) -> None:
		self.auth_success = False
		self.running = False
		self.query_running = False
		self.ConnectionWriter.close()

	def run(self, **kwargs:dict) -> None:
		"""
			start the bot, this function will wrap self.start() into a asyncio loop.
			- This function is blocking, it only returns after stop is called
		"""
		loop:asyncio.AbstractEventLoop = asyncio.new_event_loop()
		loop.run_until_complete( self.start(**kwargs) )

	async def start(self, **kwargs:dict) -> None:
		"""
			nearly the same as self.run()
			except its not going to create a loop.
			- This function is blocking, it only returns after stop is called
		"""
		if self.running:
			raise RuntimeError("already running")

		self.running = True
		self.query_running = True

		if not self.token:
			self.token = kwargs.get('token', None)
		if not self.nickname:
			self.nickname = kwargs.get('nickname', None)

		if self.token == None or self.nickname == None:
			raise AttributeError("'token' and 'nickname' must be provided")

		await self.main()

	async def main(self) -> None:

		while self.running:

			#reset bot storage
			self.last_ping = time.time()
			self.traffic = 0
			self.query_running = True
			self.auth_success = False
			# not resetting self.stored_traffic, maybe there is something inside

			try:
				#init connection
				self.ConnectionReader, self.ConnectionWriter = await asyncio.open_connection(host=self.host, port=self.port)

				#login
				await sendPass(self)
				await sendNick(self)

				#start listen
				asyncio.ensure_future( trafficQuery(self) )
				await self.listen()

			except InvalidAuth as E:
				self.stop()
				await self.onError(E)

			except EmptyPayload as E:
				await self.onError(E)
				break

			except PingTimeout as E:
				await self.onError(E)
				break

			except KeyboardInterrupt as E:
				await self.onError(E)
				self.stop()
				break

			except Exception as E:
				await self.onError(E)
				if self.running:
					await asyncio.sleep(5)
				else:
					break

	async def listen(self):

		#listen to osu
		while self.running:

			payload:bytes = await self.ConnectionReader.readline()
			asyncio.ensure_future( self.onRaw(payload) )
			payload:str = payload.decode('UTF-8').strip("\n").strip("\r")

			#just to be sure
			if payload in ["", " ", None] or not payload: raise EmptyPayload()

			# last ping is over 6min (way over osu's normal response)
			if (time.time() - self.last_ping) > 60*6:
				raise PingTimeout()

			# ignore QUIT for now
			# there are just to many... maybe someday made something with this
			if 'cho@ppy.sh QUIT' in payload:
				continue

			#response to PING
			elif re.match(RePing, payload) != None:
				self.last_ping = time.time()
				await sendPong(self)

			#onMessage
			elif re.match(ReOnMessage, payload) != None:
				await handleOnMessage(self, payload)

			#onReady
			elif re.match(ReOnReady, payload) != None:
				if self.auth_success:
					#means we got a reconnect
					asyncio.ensure_future( self.onReconnect() )
				self.auth_success = True
				asyncio.ensure_future( self.onReady() )

			elif not self.auth_success:
				if re.match(ReWrongAuth, payload) != None:
					raise InvalidAuth( payload )

	async def sendContent(self, content:bytes or str, ignore_limit:bool=False) -> None:
		"""
			used to send content of any type to osu
		"""
		if type(content) != bytes:
			content = bytes(content, 'UTF-8')

		if (self.traffic <= self.request_limit) or ignore_limit:
			asyncio.ensure_future( addTraffic(self) )
			self.ConnectionWriter.write( content )

		else:
			asyncio.ensure_future( self.onLimit(content) )
			self.stored_traffic.append( content )

	#events
	async def onError(self, Ex:Exception) -> None:
		"""
			called every time something goes wrong
		"""
		print(Ex)
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
			called when the client received a message in a channel
		"""
		pass


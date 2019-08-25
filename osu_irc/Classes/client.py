import time
import asyncio
import traceback
import re

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
				self.last_ping = time.time()
				self.query_running = True
				asyncio.ensure_future(self.send_query())
				self.auth_success = False
				await self.listen()

			except self.InvalidAuth as e:
				self.stop()
				await self.on_error(e)

			except self.EmptyPayload as e:
				await self.on_error(e)
				break

			except self.PingTimeout as e:
				await self.on_error(e)
				break

			except Exception as e:
				await self.on_error(e)
				if self.running:
					await asyncio.sleep(5)
				else:
					break

	async def listen(self):

		#listen to osu
		while self.running:

			payload = await self.connection_reader.readline()
			asyncio.ensure_future( self.on_raw_data(payload) )
			payload = payload.decode('UTF-8').strip("\n").strip("\r")

			#just to be sure
			if payload in ["", " ", None]: raise self.EmptyPayload()

			# last ping is over 6min (way over osu's normal response)
			if (time.time() - self.last_ping) > 60*6: raise self.PingTimeout()

			# ignore QUIT for now
			# there are just to many... maybe someday made something with this
			if 'cho@ppy.sh QUIT' in payload:
				continue

			#response to PING
			if re.match(Regex.ping, payload) != None:
				self.last_ping = time.time()
				await self.send_pong()

			#wrong_auth
			elif not self.auth_success and re.match(Regex.wrong_auth, payload) != None:
				raise self.InvalidAuth(str(payload))

			#on_ready
			elif re.match(Regex.on_ready, payload) != None:
				if self.auth_success: #means we got a reconnect
					asyncio.ensure_future( self.on_reconnect() )
				self.auth_success = True
				asyncio.ensure_future( self.on_ready() )

			#on_message
			elif re.match(Regex.on_message, payload) != None:
				await self.handle_on_message(payload)
	#events
	async def on_error(self, exeception):
		"""
		Attributes:
		`exeception`  =  type :: Exeception

		called every time something goes wrong
		"""
		print(exeception)
		traceback.print_exc()

	async def on_limit(self):
		"""
		Attributes:
		None

		called every time a request was not send because it hit the limit,
		the request is stored and send as soon as possible
		"""
		pass

	async def on_raw_data(self, raw):
		"""
		Attributes:
		`raw`  =  type :: bytes

		called every time some bytes of data get received by the client
		"""
		pass

	async def on_ready(self):
		"""
		Attributes:
		None

		called when the client is connected to osu and is ready to receive or send data
		"""
		pass

	async def on_reconnect(self):
		"""
		Attributes:
		None

		called when the client is reconnected, is always followed by on_ready
		"""
		pass

	async def on_message(self, message):
		"""
		Attributes:
		`message` = object :: Message

		called when the client received a message in a channel
		"""
		pass

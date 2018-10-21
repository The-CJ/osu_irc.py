# -*- coding: utf-8 -*-

"""
##################
osu! IRC wrapper
##################

Simple to use IRC connection for osu optimited for the PhaazeOS project
but usable to any purpose

:copyright: (c) 2018-2018 The_CJ
:license: MIT License

- Inspired by the code of Rapptz's Discord library (function names and usage)
- Basicly a copy of my twitch_irc library, just for osu!

"""

import asyncio, time, re, traceback

from .regex import Regex

class Client():
	#system utils
	from .utils import send_pass, send_nick, send_content, add_traffic, send_query, send_pong

	#commands
	from .commands import send_message, join_channel, part_channel

	#handler
	from .handler import handle_on_message

	def __init__(self, token=None, nickname=None):

		self.auth_success = False
		self.running = False
		self.query_running = False

		self.token = token
		self.nickname = nickname
		self.host = "irc.ppy.sh"
		self.port = 6667
		self.last_ping = time.time()

		self.connection_reader = None
		self.connection_writer = None

		self.traffic = 0
		self.stored_traffic = list()

	def stop(self):
		self.running = False
		self.query_running = False
		self.connection_writer.close()

	def run(self, **kwargs):
		self.running = True
		self.query_running = True

		self.token = kwargs.get('token', None)
		self.nickname = kwargs.get('nickname', None)

		if self.token == None or self.nickname == None:
			raise AttributeError("'token' and 'nickname' must be provided")

		loop = asyncio.get_event_loop()
		loop.run_until_complete(self.start())

	async def start(self):

		while self.running:

			#reset bot storage
			self.last_ping = time.time()
			self.traffic = 0

			try:
				#init connection
				self.connection_reader, self.connection_writer = await asyncio.open_connection(host=self.host, port=self.port)

				#login
				await self.send_pass()
				await self.send_nick()

				#start listen
				self.last_ping = time.time()
				self.query_running = True
				asyncio.ensure_future(self.send_query())
				self.auth_success = False
				await self.listen()

			except Exception as e:
				self.connection_writer.close()
				self.query_running = False
				await self.on_error(e)
				await asyncio.sleep(5)

	async def listen(self):

		#listen to osu
		while self.running:

			payload = await self.connection_reader.readuntil(separator=b'\n')
			asyncio.ensure_future( self.on_raw_data(payload) )
			payload = payload.decode('UTF-8').strip("\n").strip("\r")

			#just to be sure
			if payload in ["", " ", None]: raise ConnectionResetError()

			# last ping is over 6min (way over twitch normal response)
			if (time.time() - self.last_ping) > 60*6: raise ConnectionResetError()

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
				asyncio.ensure_future( self.on_error(ConnectionRefusedError("wrong_auth")) )
				self.stop()

			#on_ready
			elif re.match(Regex.on_ready, payload) != None:
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

	async def on_message(self, message):
		"""
		Attributes:
		`message` = object :: Message

		called when the client received a message in a channel
		"""
		pass


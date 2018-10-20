import asyncio

async def send_content(self, content, ignore_limit=False):
	""" used to send content of any type to twitch """
	if self.traffic <= 19 or ignore_limit:
		self.traffic += 1
		asyncio.ensure_future( self.add_traffic() )
		if type(content) != bytes:
			content = bytes(content, 'UTF-8')
		self.connection_writer.write(content)

	else:
		asyncio.ensure_future(self.on_limit())
		self.stored_traffic.append( content )

async def add_traffic(self):
	""" called after any send_content to reset the traffic """
	await asyncio.sleep(30)
	if self.traffic <= 0: self.traffic = 0
	else: self.traffic -= 1

async def send_query(self):
	""" get started on Cient.run(), a coro thats takes all requests that would be over the limit and send them later """
	while self.running and self.query_running:
		if self.traffic <= 18 and len(self.stored_traffic) > 0:
			req = self.stored_traffic.pop(0)
			await self.send_content( req )
		else:
			await asyncio.sleep(0.05)

# # # # #

async def send_pong(self):
	await self.send_content( "PONG :cho.ppy.sh\r\n", ignore_limit=True )

async def send_nick(self):
	await self.send_content( "NICK {0}\r\n".format(self.nickname), ignore_limit=True )

async def send_pass(self):
	await self.send_content( "PASS {0}\r\n".format(self.token), ignore_limit=True )

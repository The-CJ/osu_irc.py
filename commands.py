import asyncio

async def send_message(self, channel, message):
	channel = channel.lower().strip('#')
	await self.send_content( "PRIVMSG {0} :{1}\r\n".format(channel, message) )

async def send_pm(self, user, message):
	user = user.lower().strip('#')
	await self.send_content( "PRIVMSG {0} :{1}\r\n".format(user, message) )

async def join_channel(self, channel):
	channel = channel.lower().strip('#')
	await self.send_content( "JOIN #{0}\r\n".format(channel) )

async def part_channel(self, channel):
	channel = channel.lower().strip('#')
	await self.send_content( "PART #{0}\r\n".format(channel) )


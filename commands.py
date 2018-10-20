import asyncio

async def send_message(self, channel, message):
	channel = channel.lower().strip('#')
	await self.send_content( "PRIVMSG #{0} :{1}\r\n".format(channel, message) )


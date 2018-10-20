import asyncio
from .message import Message 

async def handle_on_message(self, payload):
	"""
	handles all messages and calls
	`self.on_message(message)` for custom user code
	"""

	# generate message
	message = Message(payload)

	asyncio.ensure_future( self.on_message( message ) )


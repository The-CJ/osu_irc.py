import re

ReUsername:"re.Pattern" = re.compile(r'^:(.+?)!')
ReRoomName:"re.Pattern" = re.compile(r'PRIVMSG (.+?) :')
ReContent:"re.Pattern" = re.compile(r'^:.+? :(.+)')

class Message(object):
	"""
		This class is generated when a user is sending a message, it turns raw data like:

		:The_CJ!cho@ppy.sh PRIVMSG Phaazebot :Test Message :D

		into a usable class
	"""
	def __str__(self):
		return self.content

	def __init__(self, raw:str):
		self.user_name:str = None
		self.channel_name:str = None
		self.channel_type:str = None
		self.content:str = None

		self.build(raw)

	def build(self, raw:str):
		#user_name
		search = re.search(ReUsername, raw)
		if search != None:
			self.name = search.group(1)

		#channel_name
		search = re.search(ReRoomName, raw)
		if search != None:
			self.channel_name = search.group(1)

		#content
		search = re.search(ReContent, raw)
		if search != None:
			self.content = search.group(1)

		#type
		if type(self.channel_name) is str:
			if self.channel_name.startswith('#'):
				self.channel_type = "channel"
			else:
				self.channel_type = "pm"

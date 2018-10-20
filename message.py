from .regex import Regex
import re

class Message(object):
	""" This class is generated when a user is sending a message, it turns raw data like:

		`raw_data` = type :: str

        :The_CJ!cho@ppy.sh PRIVMSG Phaazebot :Test Message :D

		into a usable class
	"""
	def __str__(self):
		return self.content

	def __init__(self, raw_data):
		self.raw = raw_data           				# str

		self.name = None 							# str
		self.channel_name = None					# str
		self.content = None 						# str
		self.type = None							# "pm" | "channel"

		self.process()
		del self.raw

	def process(self):
		#username
		search = re.search(Regex.Message.username, self.raw)
		if search != None:
			self.name = search.group(1)

		#channel_name
		search = re.search(Regex.Message.channel_name, self.raw)
		if search != None:
			self.channel_name = search.group(1)

		#content
		search = re.search(Regex.Message.content, self.raw)
		if search != None:
			self.content = search.group(1)

		#type
		if type(self.channel_name) == str and self.channel_name.startswith("#"):
			self.type = "channel"
		else:
			self.type = "pm"



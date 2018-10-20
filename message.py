from .regex import Regex

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
		self.content = None 						# str

		self.process()
		del self.raw

	def process(self):
		#username
		search = re.search(Regex.Message.username, self.raw)
		if search != None:
			self.name = search.group(1)

		#content
		search = re.search(Regex.Message.content, self.raw)
		if search != None:
			self.content = search.group(1)


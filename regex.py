import re

class Regex(object):
	""" Includes a precompiled re objects for every IRC event  """

	ping = re.compile(r"^PING")
	on_ready = re.compile(r"^:cho\.ppy\.sh 001.*")
	wrong_auth = re.compile(r"^:cho\.ppy\.sh 464.*")
	on_message = re.compile(r"^:(.+?)!cho\@ppy\.sh PRIVMSG .+? :.*")

	class Message(object):
		username = re.compile(r'^:(.+?)!')
		channel_name = re.compile(r'PRIVMSG (.+?) :')
		content = re.compile(r'^:.+? :(.+)')

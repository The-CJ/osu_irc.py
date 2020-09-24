class UserStore(dict):
	"""
	This is just a small little class that should make vars(Channel) more readable... no more
	"""
	def __init__(self):
		super().__init__()

	def __repr__(self):
		return f"<{self.__class__.__name__} amount={len(self)}>"

class ChannelStore(dict):
	"""
	This is just a small little class that should make vars(Client) more readable... no more
	"""
	def __init__(self):
		super().__init__()

	def __repr__(self):
		return f"<{self.__class__.__name__} amount={len(self)}>"

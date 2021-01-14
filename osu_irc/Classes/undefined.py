class Undefined(object):
	"""
	This class is never (un)equal, bigger, smaller und else to everything, its nothing
	this is btw, stolen from the Phaazebot Project LUL
	"""
	def __init__(self): pass

	def __str__(self): return ""
	def __repr__(self): return "<UNDEFINED>"
	def __int__(self): return 0

	# ==
	def __eq__(self, value):
		if type(value) == Undefined: return True
		return False

	# !=
	def __ne__(self, value):
		if type(value) != Undefined: return True
		return False

	def __ge__(self, value): return False # >=
	def __gt__(self, value): return False # >

	def __le__(self, value): return False # <=
	def __lt__(self, value): return False # <

	def __bool__(self): return False # if

	# for, in
	def __iter__(self): return self
	def __next__(self): raise StopIteration


# a constant class of undefined... so you don't need to generate new objects...
# or so? is this saving resources... idk
UNDEFINED:Undefined = Undefined()

class InvalidAuth(Exception):
	"""
	Raised when osu gives us an error login response.
	Don't get confused with `InvalidCredentials`, where osu don't even takes with us.
	"""

class InvalidCredentials(Exception):
	"""
	Raised when osu refuses to talk with us.
	This only happens when the credentials are in a invalid syntax.
	"""

class PingTimeout(Exception):
	"""
	Raised when osu didn't responded with a PING in some time.
	Most likely means something on osu's site is broken.
	"""

class EmptyPayload(Exception):
	"""
	Raised when osu sent empty data.
	Most likely means we lost connection without getting a event for it.
	"""

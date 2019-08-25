import re

RePing:"re.Pattern" = re.compile(r"^PING")
ReOnReady:"re.Pattern" = re.compile(r"^:cho\.ppy\.sh 001.*")
ReWrongAuth:"re.Pattern" = re.compile(r"^:cho\.ppy\.sh 464.*")
ReOnMessage:"re.Pattern" = re.compile(r"^:(.+?)!cho\@ppy\.sh PRIVMSG .+? :.*")

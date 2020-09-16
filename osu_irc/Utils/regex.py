import re

RePing:"re.Pattern" = re.compile(r"^PING.*")
ReOnReady:"re.Pattern" = re.compile(r"^:cho\.ppy\.sh 001.*")
ReGarbage:"re.Pattern" = re.compile(r"^.*cho\.ppy\.sh (375|372|376).*")
ReWrongAuth:"re.Pattern" = re.compile(r"^:cho\.ppy\.sh 464.*")
ReOnMessage:"re.Pattern" = re.compile(r"^:(.+?)!cho\@ppy\.sh PRIVMSG .+? :.*")

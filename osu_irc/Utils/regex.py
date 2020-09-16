import re

RePing:"re.Pattern" = re.compile(r"^PING.*")
ReOnReady:"re.Pattern" = re.compile(r"^:cho\.ppy\.sh 001.*")
ReGarbage:"re.Pattern" = re.compile(r"^.*cho\.ppy\.sh (375|372|376).*")
ReWrongAuth:"re.Pattern" = re.compile(r"^:cho\.ppy\.sh 464.*")
ReJoin:"re.Pattern" = re.compile(r"^:(.+?)!cho\@ppy\.sh JOIN :(.+?)")
RePart:"re.Pattern" = re.compile(r"^:(.+?)!cho\@ppy\.sh PART :(.+?)")
ReQuit:"re.Pattern" = re.compile(r"^:(.+?)!cho\@ppy\.sh QUIT :(.+?)")
ReUserList:"re.Pattern" = re.compile(r"^:cho\.ppy\.sh 353.*")
RePrivMessage:"re.Pattern" = re.compile(r"^:(.+?)!cho\@ppy\.sh PRIVMSG .+? :.*")

ReUserListData:"re.Pattern" = re.compile(r".*353 .* = #(\S+?) :(.*)$")
ReAction:"re.Pattern" = re.compile(r"\x01{1}ACTION (.+?)\x01{1}")

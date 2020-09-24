import re

# IRC events
RePing:"re.Pattern" = re.compile(r"^PING.*")
ReOnReady:"re.Pattern" = re.compile(r"^:cho\.ppy\.sh 001.*")
ReGarbage:"re.Pattern" = re.compile(r"^.*cho\.ppy\.sh (333|366|375|372|376).*")
ReWrongAuth:"re.Pattern" = re.compile(r"^:cho\.ppy\.sh 464.*")
ReJoin:"re.Pattern" = re.compile(r"^:(.+?)!cho\@ppy\.sh JOIN :(.+)")
RePart:"re.Pattern" = re.compile(r"^:(.+?)!cho\@ppy\.sh PART :(.+)")
ReQuit:"re.Pattern" = re.compile(r"^:(.+?)!cho\@ppy\.sh QUIT :(.+)")
ReUserList:"re.Pattern" = re.compile(r"^:cho\.ppy\.sh 353.*")
ReMOTD:"re.Pattern" = re.compile(r"^:cho\.ppy\.sh 332.*")
ReMode:"re.Pattern" = re.compile(r"^:.+?!cho\@cho.ppy\.sh MODE .+")
RePrivMessage:"re.Pattern" = re.compile(r"^:.+?!cho\@ppy\.sh PRIVMSG .+? :.*")

# extended IRC Events
ReUserListData:"re.Pattern" = re.compile(r".*353 .* = (#?\S+?) :(.*)$")
ReMOTDInfo:"re.Pattern" = re.compile(r"^:cho\.ppy\.sh 332 .+ (#?\S+) :(.+)$")
ReModeInfo:"re.Pattern" = re.compile(r"^:.+?!cho\@cho.ppy\.sh MODE (#?\S+?) (\+|-)(o|v) (\S+)$")
ReAction:"re.Pattern" = re.compile(r"\x01{1}ACTION (.+?)\x01{1}")

# other
ReUserName:"re.Pattern" = re.compile(r"(?:@|;| |^):(\S*?)!cho@ppy.sh[; ]")
ReRoomName:"re.Pattern" = re.compile(r"[@; ][A-Z]+ :?(#?\S+?)(?:[; ]|$)")
ReContent:"re.Pattern" = re.compile(r"[@; ][A-Z]+ #?\S+? :(.+)(?:[; ]|$)")

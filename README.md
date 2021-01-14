# osu! irc Client

Simple to use IRC connection for Osu! optimized for the PhaazeOS project
but usable to any purpose

> Inspired by the code of Rapptz's Discord library (function names and usage)

## Install

There are many ways. here my "preferred" one:
```
py -m pip install git+https://github.com/The-CJ/osu_irc.py.git#egg=osu_irc
```

## Example

```py
import osu_irc

class MyBot(osu_irc.Client):

  async def onReady(self):
    self.joinChannel("#osu")
    #do something

  async def onMessage(self, message):
    print(message.content)

    # do more with your code


x = MyBot(token="1234567890", nickname="cool_username")
x.run()
```
Get nickname and server password(token) from here: https://osu.ppy.sh/p/irc
:copyright: 2018-2021 The_CJ

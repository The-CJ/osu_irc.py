# osu! irc Client

Simple to use IRC connection for Osu! optimited for the PhaazeOS project
but usable to any purpose


> Inspired by the code of Rapptz's Discord library (function names and usage)

## Usage

```
import asyncio, osu_irc

class MyBot(osu_irc.Client):

  async def on_ready(self):
    #do something

  async def on_message(self, message):
    print(message.content)

    # do more with your code


x = MyBot()
x.run(token="supersecret", nickname="cool_username")
```
:copyright: 2018-2018 The_CJ

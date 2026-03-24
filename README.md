# session

# What is This?

I have provided a discord bot's code, written in Python, which might help you with cleaning your nuked server. This can delete roles, emojis, webhooks, and much more. Place the bot's role above the spam created roles, and it will delete those.

# What if someone uses this to nuke servers?

They must have administrator permissions to perform some dangerous actions, and we support a blacklist system, too. You can blacklist those who ain't trusted, and can nuke your server. 

# Installation
You must have the latest version of discord.py installed in order to run this, because this uses the discord's ui.LayoutView which is new. Do ``pip install -r requirements.txt``, That will install the latest versions of modules used in the code. 

`` git clone https://github.com/wjpg1/session.git ``
`` cd session ``
`` python3 main.py `` or `` cd CodeInOneFile `` - ``python3 bot.py``

You can run this easily in other code-editors like: pydroid3 by copy-pasting the "CodeInOneFile" folder's bot.py, you must provide your bot's token, and change the bot's prefix, if wanted. The prefix is ``!`` by default.

# ``Session's available commands`` :
 ## ``Cleanup`` :
`` {your_prefix} or !help - aliases: hlp - shows the commands's help menu``

`` {your_prefix} or !cleanup - aliases: wipe, cln - deletes the server's emojis, stickers, webhooks, and roles. ``

`` {your_prefix} or !deletewebhooks - aliases: dw, delweb - deletes the server's webhooks. ``

`` {your_prefix} or !deleteroles - aliases: dr, delroles - deletes the server's roles. ``

`` {your_prefix} or !deleteemojis - aliases: de, delemo - deletes the server's emojis ``

`` {your_prefix} or !deletestickers - aliases: ds, delsti - deletes the server's stickers. ``

`` {your_prefix} or !delete

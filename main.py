import discord, requests, psutil, sys, time, datetime
from discord.ext import commands
from ezlib import *

nullTime = time.time()




class Main(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.cooldown(3, 10, commands.BucketType.guild)
	async def clear(self, ctx, limit: int):
		if 100 >= limit >= 10:
			messages = await ctx.channel.history(limit=limit).flatten()
			deleted = 0
			for message in messages:
				if await scan_message(message, notify=False):
					deleted += 1
			await done(ctx, f"Deleted {deleted} messages.")
		else:
			await fail(ctx, f"The number of messages should be in the range from 10 to 100.")

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def clearall(self, ctx, limit: int):
		if 100 >= limit >= 10:
			deleted = 0
			for channel in ctx.guild.text_channels:
				messages = await channel.history(limit=limit).flatten()
				for message in messages:
					if await scan_message(message, notify=False):
						deleted += 1
			await done(ctx, f"Deleted {deleted} messages.")
		else:
			await fail(ctx, f"The number of messages should be in the range from 10 to 100.")

	@commands.command()
	@commands.cooldown(1, 30, commands.BucketType.user)
	async def report(self, ctx, *, message):
		avatar = str(ctx.author.avatar_url)
		payload = {"embeds": [{"description": message,
				   "color": 0xff6060, "footer": {
						"text": str(ctx.author),
						"icon_url": avatar
						}}]}
		requests.post(hook, json=payload)
		await done(ctx, "Your message has been sent to the support server.")


	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def disable(self, ctx):
		db = db_read()
		disabled = db.get("disabled", [])
		key = ctx.guild.id
		if key not in disabled:
			db["disabled"].append(key)
			db_write(db)
			await done(ctx, "Message scannin has been disabled.")
		else:
			return await fail(ctx, f"Message scanning is already disabled on this server.")


	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def enable(self, ctx):
		db = db_read()
		key = ctx.guild.id
		if key in db.get("disabled", []):
			db["disabled"].remove(key)
			db_write(db)
			await done(ctx, "Message scanning has been enabled.")
		else:
			return await fail(ctx, f"Message scanning is already enabled on this server.")


	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def remlogs(self, ctx):
		db = db_read()
		key = ctx.guild.id
		if key in db.get("logchannels", {}):
			del db["logchannels"][key]
			db_write(db)
			await done(ctx, "Logs will be sent to the same channel in which the message was deleted.")
		else:
			return await fail(ctx, f"Sending logs to a separate channel is already disabled on this server.")

	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def setlogs(self, ctx, channel: discord.TextChannel):
		db = db_read()
		key: int = ctx.guild.id
		cid = channel.id
		db["logchannels"].get(key)
		db["logchannels"][key] = cid
		db_write(db)
		await done(ctx, f"Logs will be sent to {channel.mention}.")


	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def disabledms(self, ctx):
		db = db_read()
		disabled = db.get("nodms", [])
		key = ctx.guild.id
		if key not in disabled:
			db["nodms"].append(key)
			db_write(db)
			await done(ctx, "Sending private messages to users has been disabled.")
		else:
			return await fail(ctx, f"Sending private messages to users is already disabled on this server.")

	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def enabledms(self, ctx):
		db = db_read()
		disabled = db.get("nodms", [])
		key = ctx.guild.id
		if key in disabled:
			db["nodms"].remove(key)
			db_write(db)
			await done(ctx, "Sending private messages to users has been enabled.")
		else:
			return await fail(ctx, f"Sending private messages to users is already enabled on this server.")


	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def disablenotify(self, ctx):
		db = db_read()
		disabled = db.get("dontnotify", [])
		key = ctx.guild.id
		if key not in disabled:
			db["dontnotify"].append(key)
			db_write(db)
			await done(ctx, "Notifications about deleting messages on this server has been disabled.")
		else:
			return await fail(ctx, f"Notifications about deleting messages are already disabled on this server.")

	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def enablenotify(self, ctx):
		db = db_read()
		disabled = db.get("dontnotify", [])
		key = ctx.guild.id
		if key in disabled:
			db["dontnotify"].remove(key)
			db_write(db)
			await done(ctx, "Notifications about deleting messages on this server has been enabled.")
		else:
			return await fail(ctx, f"Notifications about deleting messages are already enabled on this server.")




class Owner(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="eval")
	@commands.is_owner()
	async def _eval(self, ctx, *, code):
		result = eval(code, locals(), globals())
		if result:
			await ctx.send(result)

	@commands.command(name="await")
	@commands.is_owner()
	async def _await(self, ctx, *, code):
		result = await eval(code, locals(), globals())
		if result:
			await ctx.send(result)




class Info(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def status(self, ctx):
		scanner_calls = getsc()
		deleted_messages = getdmc()
		up = int(time.time() - nullTime)
		up = datetime.timedelta(seconds=up)
		ping = round(self.bot.latency * 1000, 2)
		data = f"""
```
Servers:                  {len(self.bot.guilds)}
Users:                    {len(self.bot.users)}
``````
Scanner calls:            {scanner_calls}
Deleted messages:         {deleted_messages}
``````
Client:                   {self.bot.user}
ID:                       {self.bot.user.id}
``````
RAM usage:                {psutil.virtual_memory().percent}%
CPU usage:                {psutil.cpu_percent()}%
``````
Uptime:                   {up}
Websocket ping:       {ping} мс.
``````
Python:                   {sys.version.split('(')[0]}
discord.py:               {discord.__version__}
```
"""
		e = discord.Embed(color=0x8080ff)
		e.add_field(name="Bot status", value=data)
		e.set_thumbnail(url="https://media.discordapp.net/attachments/832662675963510827/857631236355522650/logo.png")
		await ctx.send(embed=e)

	@commands.command()
	async def about(self, ctx):
		embed = discord.Embed(color=0x8080ff,
			    	  title="Information",
			    	  description=f"""
{info} This bot is designed to protect your server from a scam with "Free Nitro for 3 months from Steam" and people allegedly distributing their CS:GO inventory. If you see such messages, do not be fooled by them!

To prevent your account from being hacked, do not use BetterDiscord and do not download suspicious software. If you have already been hacked, remove BetterDiscord from your PC, change the password and install a reliable antivirus (For example, [Kaspersky](https://kaspersky.ru)).

**Version from**: [<t:{unix}>](https://github.com/ezz-dev/scamprotect)
**Developer**: https://github.com/Sweety187
**Source code**: https://github.com/ezz-dev/scamprotect
**Our server**: https://discord.gg/GpedR6jeZR
**Donate**: https://qiwi.com/n/XF765
""")
		embed.set_footer(text="Thanks for using our bot!")
		embed.set_image(url="https://media.discordapp.net/attachments/832662675963510827/888101822370308117/unknown.png")
		await ctx.send(embed=embed)

	@commands.command()
	async def invite(self, ctx):
		link = f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot"
		embed = discord.Embed(description=f"{info} Add me to your server: [[Invite]]({link})",
							  color=0x8080ff)
		await ctx.send(embed=embed)

	@commands.command()
	async def help(self, ctx):
		embed = discord.Embed(title="Welcome!", color=0x8080ff)
		embed.add_field(name="🧭 Information", value=f"""
`~help` - Shows this messages
`~status` - The technical condition of the bot and its statistics.
`~invite` - Get bot invite link.
`~about` - Information about the bot and its developers.
""".replace("~", ctx.prefix), inline=False)
		embed.add_field(name="🛠️ Tools", value=f"""
`~clear <limit>` - Scan N-amount of messages in this channel.
`~clearall <limit>` - Scan N-amount of messages in all channels.
`~report <message>` - Report a link/message.
""".replace("~", ctx.prefix), inline=False)
		embed.add_field(name="⚙️ Settings", value=f"""
`~prefix` - Change the command prefix for this server.
`~enable` - Enable message scanning.
`~disable` - Disable message scanning.
`~enabledms` - Enable notifications in private messages.
`~disabledms` - Disable notifications in private messages.
`~enablenotify` - Enable notifications on the server.
`~disablenotify` - Disable notifications on the server.
`~remlogs` - Disable sending notifications to a separate channel.
`~setlogs` - Set the channel for sending notifications.
""".replace("~", ctx.prefix), inline=False)
		embed.set_footer(icon_url=self.bot.user.avatar_url,
						 text="© 2021, Ezz Development | https://github.com/ezz-dev")
		await ctx.send(embed=embed)




def setup(bot):
	bot.add_cog(Main(bot))
	bot.add_cog(Owner(bot))
	bot.add_cog(Info(bot))

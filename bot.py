import discord, asyncio, re
from discord.ext import commands

bot = commands.Bot(command_prefix='!', intents=discord.Intents().all(),
		   case_insensitive=True, help_command=None)
Token = "TOKEN"
embed_blacklist = ["discord nitro бесплатно на 3 месяца от steam", "сделайте discord ещё круче с nitro",
		   "3 months of discord nitro free from steam", "get 3 months of discord nitro free from steam",
		   "discord nitro for 3 months with steam", "free discord nitro for 3 months from steam",
		   "make discord even cooler with nitro"]
patterns_blacklist = [r"i'm leaving.*skin.*http", r"i'm leaving.*inventory.*http",
                      r"i am leaving.*trade.*http", r"i leave.*trade.*http",
		      r"@everyone.*nitro.*free.*steam.*http"]
reasons = ["blacklist.link: {}", "blacklist.embed: {}", "blacklist.pattern: {}"]

with open("blacklist.txt") as file:
	_text_ = file.read()
	blacklist = _text_.split("\n")


@bot.command()
async def invite(ctx):
	link = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot"
	embed = discord.Embed(description=f":small_blue_diamond: Add me to your server: [[Invite]]({link})")
	await ctx.send(embed=embed)


@bot.event
async def on_ready():
	print("Logged in.")
	presence = f'{bot.command_prefix}invite | [{len(bot.guilds)}]'
	await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(presence))


@bot.event
async def on_message(message):
	if message.author.bot:
		return
	await bot.process_commands(message)
	await scan_message(message)


async def scan_message(message):
	index = 0
	for elem in blacklist:
		if elem in message.content.lower() and elem != "":
			return await delete(message, index, 0, 0, "message.content")
		index += 1
	index = 0
	for elem in patterns_blacklist:
		if re.findall(elem, message.content.lower().replace("\n", " ")):
			return await delete(message, index, 0, 2, "message.content")
		index += 1
	if not message.embeds and "http" in message.content:
		await asyncio.sleep(1)
		message = await message.channel.fetch_message(message.id)
	index = 0
	for embed in message.embeds:
		if await check_embed(embed, message, index):
			return
		index += 1


async def check_embed(embed, message, index):
	indexx = 0
	for elem in embed_blacklist:
		try:
			if elem in embed.title.lower() and elem != "":
				return await delete(message, index, indexx, 1, "title")
		except:
			return False
		try:
			if elem in embed.description.lower() and elem != "":
				return await delete(message, index, indexx, 1, "description")
		except:
			return False
		indexx += 1


async def delete(message, index, indexx, rindex, blkey):
	await message.delete()
	reason = reasons[rindex].format(f"{blkey}: {[indexx]}: {index}")
	embed = discord.Embed(description=f":warning: Deleted message from user {message.author.mention}.\n \➡ **Reason**: **`{reason}`**.")
	await message.channel.send(embed=embed)
	embed = discord.Embed(description=f":warning: **Your message has been deleted**.\n```{message.content}```")
	embed.set_footer(text="Most likely, you have become a victim of hacking and your account has been used for scam attacks. To prevent this from happening again, please change your password, delete BetterDiscord from your PC and use a reliable antivirus.")
	await message.author.send(embed=embed)


bot.run(Token)

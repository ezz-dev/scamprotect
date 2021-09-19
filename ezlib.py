import discord, re, pathlib, asyncio, json, requests

embed_blacklist = ["discord nitro бесплатно на 3 месяца от steam", "сделайте discord ещё круче с nitro",
		   		   "3 months of discord nitro free from steam", "get 3 months of discord nitro free from steam",
		   		   "discord nitro for 3 months with steam", "free discord nitro for 3 months from steam",
		   		   "make discord even cooler with nitro"]
patterns_blacklist = [r"i'm leaving.*skin.*http", r"i'm leaving.*inventory.*http",
                      r"i am leaving.*trade.*http", r"i leave.*trade.*http",
                      r"@everyone.*nitro.*free.*steam.*http", r"i am leaving.*away.*skins.*http"]
reasons = ["blacklist.link: {}", "blacklist.embed: {}", "blacklist.pattern: {}"]
unix = int(pathlib.Path('bot.py').stat().st_mtime)

info = "<:emoji:000000000000000000>"
danger = "<:emoji:000000000000000000>"
vmark = "<:emoji:000000000000000000>"
xmark = "<:emoji:000000000000000000>"

InetSession = requests.Session()
dbtoken = "API_TOKEN"
prefixes = {}
default_prefix = "!"

hook = "https://discord.com/api/webhooks/000000000000000000/WEBHOOK_TOKEN"


async def determine_prefix(bot, message):
	key = message.guild.id
	return get_prefix(key)


def get_prefix(key):
	prefix = prefixes.get(key)
	if prefix:
		return prefix
	db = db_read()
	prefix = db["prefixes"].get(str(key))
	if prefix:
		prefixes[key] = prefix
		return prefix
	prefixes[key] = default_prefix
	return default_prefix

def set_prefix(key, prefix):
	prefixes.get(id)
	prefixes[key] = prefix
	db = db_read()
	db["prefixes"].update({key: prefix})
	db_write(db)


with open("blacklist.txt") as file:
	_text_ = file.read()
	blacklist = _text_.split("\n")


def update_session():
	session = open("session.json", "w+")
	session.truncate()
	session.write(json.dumps(sessioncache))
	session.close()


def get_session():
	session = open("session.json", "r")
	content = str(session.read())
	session.close()
	return eval(content)


sessioncache: dict = get_session()
update_session()


def getsc():
	data = get_session()
	return data["sc"]


def getdmc():
	data = get_session()
	return data["dmc"]


async def scan_message(message, notify=False, cid=None, dm=None):
	sc = sessioncache["sc"]
	sessioncache["sc"] = sc + 1
	update_session()
	index = 0
	for elem in blacklist:
		if elem in message.content.lower() and elem != "":
			return await delete(message, index, 0, 0, "message.content", notify=notify, cid=cid, dm=dm)
		index += 1
	index = 0
	for elem in patterns_blacklist:
		if re.findall(elem, message.content.lower().replace("\n", " ")):
			return await delete(message, index, 0, 2, "message.content", notify=notify, cid=cid, dm=dm)
		index += 1
	if not message.embeds and "http" in message.content:
		await asyncio.sleep(1)
		message = await message.channel.fetch_message(message.id)
	index = 0
	for embed in message.embeds:
		if await check_embed(embed, message, index, notify=notify, cid=cid, dm=dm):
			return True
		index += 1


async def check_embed(embed, message, index, notify=False, cid=None, dm=None):
	indexx = 0
	for elem in embed_blacklist:
		try:
			if elem in embed.title.lower() and elem != "":
				return await delete(message, index, indexx, 1, "title", notify=notify, cid=cid, dm=dm)
		except:
			return False
		try:
			if elem in embed.description.lower() and elem != "":
				return await delete(message, index, indexx, 1, "description", notify=notify, cid=cid, dm=dm)
		except:
			return False
		indexx += 1


async def delete(message, index, indexx, rindex, blkey, notify: bool=False, cid=None, dm=None):
	reason = reasons[rindex].format(f"{blkey}: {[indexx]}: {index}")
	embed1 = discord.Embed(description=f"{danger} Deleted message from user {message.author.mention}.\n 》 **Reason**: **`{reason}`**.",
			       color=0xff6060)
	embed2 = discord.Embed(description=f"{danger} **Your message has been deleted**.\n```{message.content}```",
			       color=0xff6060)
	embed2.set_footer(text="Most likely, you have become a victim of hacking and your account was used for scam attacks. To prevent this from happening again, delete BetterDiscord from your PC, change the password and use a reliable antivirus.")
	dmc = sessioncache["dmc"]
	sessioncache["dmc"] = dmc + 1
	update_session()
	try:
		await message.delete()
		if notify:
			channel = message.channel
			if cid:
				channel = discord.utils.get(message.guild.text_channels, id=cid)
			if not channel or not cid:
				channel = message.channel
			await channel.send(embed=embed1)
			if dm:
				await message.author.send(embed=embed2)
	except Exception as e:
		print(e)
		return False
	return True


def db_read():
	response = InetSession.get(f"https://example.com/api/server.php?token={dbtoken}&do=getdb")
	return json.loads(response.text)


def db_write(data: dict):
	data = json.dumps(data)
	InetSession.get(f"https://example.com/api/server.php?token={dbtoken}&do=setdb&data={data}")


async def done(ctx, message):
	return await ctx.send(f"{vmark} {message}")


async def fail(ctx, message):
	return await ctx.send(f"{xmark} {message}")


async def presence_loop(bot):
	while True:
		presence = f"{default_prefix}help | [{len(bot.guilds)}]"
		await bot.change_presence(status=discord.Status.idle,
								  activity=discord.Activity(name=presence,
								  							type=discord.ActivityType.watching))
		await asyncio.sleep(10)

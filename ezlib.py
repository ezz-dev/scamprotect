import discord
import re
import pathlib
import asyncio
import json
import requests


reasons = ["Link: {}", "Embed: {}", "Pattern: {}"]
unix    = int(pathlib.Path('bot.py').stat().st_mtime)

__version__ = "4.8.1"

info   = "<:emoji:000000000000000000>"
danger = "<:emoji:000000000000000000>"
vmark  = "<:emoji:000000000000000000>"
xmark  = "<:emoji:000000000000000000>"

PRIMARY   = 0x000000
SECONDARY = 0x000000

InetSession    = requests.Session()
api_key        = "API_TOKEN"
api_url        = f"http://example.com/api/server.php?token={api_key}&"
base_url       = "http://example.com"
prefixes       = {}
default_prefix = "!"

hook = "https://discord.com/api/webhooks/000000000000000000/WEBHOOK_TOKEN"


def api_interact(do: str, data=None):
	print(f"[API interaction] {do}: {data}")
	result   = None
	data     = json.dumps(data)
	response = InetSession.get(f"{api_url}do={do}&data={data}", timeout=10)
	if response.text:
		result = json.loads(response.text)
	return result




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




def get_session():
	with open("session.json", "r") as session:
		content = session.read()
	return json.loads(content)


def reset_session():
	with open("session.json", "w+") as session:
		session.truncate()
		session.write(json.dumps({"sc": 0, "dmc": 0}))


def update_session():
	with open("session.json", "w+") as session:
		session.truncate()
		session.write(json.dumps(sessioncache))


def get_remote_session():
	print("[EzLib] Getting remote session...")
	response = InetSession.get(f"{base_url}/session.json", timeout=10)
	return json.loads(response.text)


def get_global_session():
	print("[EzLib] Getting global session...")
	external_session = get_remote_session()
	local_session    = get_session()

	local_sc  = local_session["sc"]
	local_dmc = local_session["dmc"]

	external_sc  = external_session["sc"]
	external_dmc = external_session["dmc"]
	
	sc  = external_sc  + local_sc
	dmc = external_dmc + local_dmc

	return {"sc": sc, "dmc": dmc}


def send_session():
	cache = get_global_session()
	api_interact("setSession", cache)
	
	with open("session.json", "w+") as session:
		cache = json.dumps(cache)
		session.truncate()
		session.write(cache)


def send_stats(data: dict):
	api_interact("setStats", data)


sessioncache = {"sc": 0, "dmc": 0}
print("[EzLib] Sending latest session...")
send_session()
print("[EzLib] Updating session...")
update_session()
print("[EzLib] Session updated.")




def getsc():
	data = get_global_session()
	return data["sc"]


def getdmc():
	data = get_global_session()
	return data["dmc"]


def sc_up():
	sc = sessioncache["sc"]
	sessioncache["sc"] += 1
	update_session()


def dmc_up():
	dmc = sessioncache["dmc"]
	sessioncache["dmc"] += 1
	update_session()


def db_read():
	return api_interact("getdb")


def db_write(data: dict):
	api_interact("setdb", data)


def fetch_scanner_arguments(key):
	db = db_read()
	dm = key not in db["nodms"]
	notify = key not in db["dontnotify"]
	disabled = db.get("disabled", [])
	cid = db["logchannels"].get(str(key))
	return dm, notify, disabled, cid




def get_patterns():
	print("[EzLib] Fetching patterns blacklist...")
	return api_interact("getPatterns")


def set_patterns(data: list):
	api_interact("setPatterns", data)


def get_eb():
	print("[EzLib] Fetching embed blacklist...")
	return api_interact("getEB")


def set_eb(data: list):
	api_interact("setEB", data)


embed_blacklist    = get_eb()
patterns_blacklist = get_patterns()
print("[EzLib] Defined blacklists.")




async def scan_message(message, notify=False, cid=None, dm=None):
	sc_up()

	index = 0
	for elem in blacklist:
		if elem in message.content.lower() and elem != "":
			return await delete(message, index, 0, 0, "Text", notify=notify, cid=cid, dm=dm)
		index += 1

	index = 0
	for elem in patterns_blacklist:
		if re.findall(elem, message.content.lower().replace("\n", " ")):
			return await delete(message, index, 0, 2, "Text", notify=notify, cid=cid, dm=dm)
		index += 1

	if not message.embeds and "http" in message.content:
		await asyncio.sleep(1)
		message = await message.channel.fetch_message(message.id)
	elif not "http" in message.content:
		return

	indexx = 0
	for embed in message.embeds:
		if await check_embed(embed, message, 0, notify=notify, cid=cid, dm=dm):
			return True
		indexx += 1


async def check_embed(embed, message, indexx, notify=False, cid=None, dm=None):
	index = 0
	for elem in embed_blacklist:
		try:
			if elem in embed.title.lower() and elem != "":
				return await delete(message, index, indexx, 1, "Title", notify=notify, cid=cid, dm=dm)
		except:
			return False
		try:
			if elem in embed.description.lower() and elem != "":
				return await delete(message, index, indexx, 1, "Description", notify=notify, cid=cid, dm=dm)
		except:
			return False
		index += 1


async def delete(message, index, indexx, rindex, blkey, notify: bool=False, cid=None, dm=None):
	reason = reasons[rindex].format(f"{blkey}: {[indexx]}: {index}")
	embed1 = discord.Embed(description=f"{danger} Deleted message from user {message.author.mention}.\n » **Reason**: **`{reason}`**.",
			       		   color=SECONDARY)
	embed2 = discord.Embed(description=f"{danger} **Your message has been deleted**.\n```{message.content}```",
			       		   color=SECONDARY)
	embed2.set_footer(text="Most likely, you have become a victim of hacking and your account was used for scam attacks. To prevent this from happening again, delete BetterDiscord from your PC, change the password and use a reliable antivirus.")
	
	try:
		await message.delete()
		if notify:
			channel = message.channel
			if cid:
				channels = message.guild.text_channels
				channel  = discord.utils.get(channels, id=cid)
			if not channel or not cid:
				channel  = message.channel
			await channel.send(embed=embed1)
			if dm:
				await message.author.send(embed=embed2)
	except:
		return False

	dmc_up()
	return True




async def done(ctx, message):
	return await ctx.send(f"{vmark} {message}")


async def fail(ctx, message):
	return await ctx.send(f"{xmark} {message}")




async def presence_loop(bot):
	while True:
		stats = {"guilds": len(bot.guilds), "users": len(bot.users)}
		send_stats(stats)

		presence = f"{default_prefix}help | [{len(bot.guilds)}]"
		await bot.change_presence(status=discord.Status.dnd,
					  activity=discord.Activity(name=presence,
								    type=discord.ActivityType.watching))
		await asyncio.sleep(60)


print(f"[EzLib] Loaded EzLib {__version__}")

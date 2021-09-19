import discord
from discord.ext import commands
from ezlib import *

bot = commands.Bot(command_prefix=determine_prefix,
		   intents=discord.Intents().all(),
		   case_insensitive=True,
		   help_command=None)
Token = "TOKEN"
bot.load_extension("main")


@bot.command()
@commands.has_permissions(manage_guild=True)
@commands.cooldown(1, 30, commands.BucketType.guild)
async def prefix(ctx, prefix):
	if len(prefix) > 5:
		return await fail(ctx, "Prefix cannot be longer than 5 charters.")
	if "`" in prefix:
		return await fail(ctx, "Prefix contains illegal charters.")
	key = ctx.guild.id
	set_prefix(key, prefix)
	await done(ctx, f"Command prefix for this server has been changed to `{prefix}`.")


@bot.event
async def on_ready():
	print("Logged in.")
	await presence_loop(bot)


@bot.event
async def on_command_error(ctx, error):
	msg = error
	if isinstance(error, commands.errors.CommandInvokeError):
		_error = str(error).replace("Command raised an exception: ", "")
		msg = f"An error has occured.\n```{_error}```"
	if isinstance(error, commands.errors.CommandNotFound):
		return
	if isinstance(error, commands.CommandOnCooldown):
		msg = f"You will able to use this command in {int(error.retry_after)} seconds."
	if isinstance(error, commands.errors.BotMissingPermissions):
		msg = "I don\'t have permissions to execute this command."
	if isinstance(error, commands.errors.MissingRequiredArgument):
		msg = "Missing required argument."
	if isinstance(error, commands.MissingPermissions):
		msg = f'You don\'t have permission to use this command.'
	return await fail(ctx, msg)


@bot.event
async def on_message(message):
	if message.author.bot:
		return
	if message.content == f"<@{bot.user.id}>":
		p = get_prefix(message.guild.id)
		await message.reply(f"{vmark} Мой префикс: [`{p}`].")
	await bot.process_commands(message)
	db = db_read()
	key = str(message.guild.id)
	key_ = message.guild.id
	dm = key_ not in db["nodms"]
	notify = key_ not in db["dontnotify"]
	disabled = db.get("disabled", [])
	cid = db["logchannels"].get(key)
	if key_ not in disabled:
		await scan_message(message, notify=notify, cid=cid, dm=dm)


bot.run(Token)

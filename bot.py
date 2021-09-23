import discord
from discord.ext import commands
from ezlib import *

bot = commands.Bot(command_prefix=determine_prefix,
		   intents=discord.Intents().all(),
		   case_insensitive=True,
		   help_command=None)
Token = "TOKEN"

print("[Main Thread] Loading Command Listener...")
bot.load_extension("main")


@bot.command()
@commands.has_permissions(manage_guild=True)
@commands.cooldown(1, 30, commands.BucketType.guild)
async def prefix(ctx, prefix):
	if len(prefix) > 5:
		return await fail(ctx, "Префикс не может быть длиннее 5 символов.")
	if "`" in prefix:
		return await fail(ctx, "Префикс содержит недопустимый символ.")
	key = ctx.guild.id
	set_prefix(key, prefix)
	await done(ctx, f"Префикс для этого сервера иземенен на `{prefix}`.")


@bot.event
async def on_ready():
	print("[Main Thread] Logged in.")
	await presence_loop(bot)


@bot.event
async def on_command_error(ctx, error):
	msg = error
	if isinstance(error, commands.errors.CommandInvokeError):
		_error = str(error).replace("Command raised an exception: ", "")
		print(f"[Main Thread] Command `{ctx.message.content}` raised an exception: `{_error}`")
		msg = f"An error has occured.\n```py\n{_error}```"
	if isinstance(error, commands.errors.CommandNotFound):
		return
	if isinstance(error, commands.CommandOnCooldown):
		msg = f"This command will be available in {int(error.retry_after)} seconds."
	if isinstance(error, commands.errors.BotMissingPermissions):
		msg = "I don't have permission to execute this command."
	if isinstance(error, commands.errors.MissingRequiredArgument):
		msg = "Missing required argument."
	if isinstance(error, commands.MissingPermissions):
		msg = f"You are missing permission to invoke this command."
	if isinstance(error, commands.errors.ChannelNotFound):
		msg = "Channel not found."
	if isinstance(error, commands.BadArgument):
		msg = "Bad argument."
	if isinstance(error, commands.errors.NotOwner):
		msg = "You can't invoke this command."
	await fail(ctx, msg)


@bot.event
async def on_message(message):
	if message.author.bot:
		return
	if message.content == f"<@!{bot.user.id}>":
		p = get_prefix(message.guild.id)
		return await message.reply(f"{vmark} My prefix: [`{p}`].")

	await bot.process_commands(message)

	key = message.guild.id
	dm, notify, disabled, cid = fetch_scanner_arguments(key)

	if key not in disabled:
		await scan_message(message, notify=notify, cid=cid, dm=dm)


print("[Main Thread] Logging in...")
bot.run(Token)

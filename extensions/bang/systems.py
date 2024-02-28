import aiomysql
import asyncio
import json
import os
import re

import discord
from discord.ext import commands

class Systems(commands.Cog, name="Systems"):
	__slots__ = (
		"bot"
	)
	def __init__(self, bot:commands.Bot) -> None:
		try:
			self.bot = bot
			self.bot.remove_command("help")
		except Exception as e:
			raise e

	@commands.command(
		description = "Ping latency of the bot",
		usage = "ping",
		hidden = True,
	)
	@commands.guild_only()
	async def ping(self, ctx:commands.Context) -> None:
		try:
			embed = self.bot.embed(
				ctx = ctx,
				title = "Ping",
				description = f"{self.bot.latency * 1000:,.0f}ms",
				bot = True,
			)
			await ctx.send(
				embed = embed,
				reference = ctx.message,
			)
		except discord.HTTPException:
			await ctx.send(
				content = f"Pong: {self.bot.latency * 1000:,.0f}ms"
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		description = "Get the bot's uptime",
		usage = "uptime",
		hidden = True,
	)
	@commands.guild_only()
	async def uptime(self, ctx:commands.Context) -> None:
		try:
			embed = self.bot.embed(
				ctx = ctx,
				title = "Uptime",
				description = f"{self.bot.uptime()}",
				bot = True,
			)
			await ctx.send(
				embed = embed,
				reference = ctx.message,
			)
		except discord.HTTPException:
			await ctx.send(
				content = f"Uptime: {self.bot.uptime()}"
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.hybrid_command(
		aliases = ["h"],
		description = "Show this help...",
		usage = "help [command/cog/extension]",
	)
	async def help(self, ctx:commands.Context, command:str = None) -> None:
		try:
			showHidden = False
			if ctx.channel.id in self.bot.get_config(ctx.guild, "channel", "staff"):
				showHidden = True
			md = "```md\n"
			if command is None:
				for cog in [c for c in self.bot.cogs.keys()]:
					cogs = self.bot.get_cog(cog).get_commands()
					if cogs is None:
						continue
					cog_md = f"# {cog}\n"
					for cmd in cogs:
						if (showHidden or (showHidden is False and cmd.hidden is False))\
						and cmd.enabled is True:
							if cog_md is not None:
								md += cog_md
								cog_md = None
							md += f"  {ctx.prefix}{cmd.name}"
							for param in cmd.clean_params:
								md += f" <{param}>"
							md += "\n"
							if not cmd.usage and cmd.brief:
								md += f" {cmd.brief}\n"
			else:
				cmd = self.bot.get_command(command)
				if cmd is None:
					md += f"Cannot find command: {command}"
				elif (showHidden or (showHidden is False and cmd.hidden is False))\
				and cmd.enabled is True:
					md += f"# {cmd.cog_name}/{cmd.qualified_name}\n"
					md += f"  {ctx.prefix}"
					if cmd.aliases:
						aliases = "|".join(cmd.aliases)
						md += f"[{cmd.name}|{aliases}]"
					else:
						md += f"{cmd.name}"
					for param in cmd.clean_params:
						md += f" <{param}>"
					md += "\n"
					if cmd.usage:
						md += f"usage: {cmd.usage}\n"
					if not cmd.usage and cmd.brief:
						md += f"brief: {cmd.brief}\n"
					if cmd.description:
						md += f"description:\n{cmd.description}\n"
					if cmd.help:
						md += f"help:\n{cmd.help}\n"
			md += "```"
			await ctx.send(
				content = md,
				reference = ctx.message,
				#delete_after = 120,
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		description = "load extension",
		hidden = True,
	)
	@commands.is_owner()
	async def load(self, ctx:commands.Context, extension:str):
		try:
			await self.bot.load_extension("extensions.bang." + extension)
			await ctx.send(
				content = f"Loaded: {extension}",
				reference = ctx.message,
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		description = "reload extension",
		hidden = True,
	)
	@commands.is_owner()
	async def reload(self, ctx:commands.Context, extension:str):
		try:
			await self.bot.reload_extension("extensions.bang." + extension)
			await ctx.send(
				content = f"Reloaded: {extension}",
				reference = ctx.message,
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		description = "unload extension",
		hidden = True,
	)
	@commands.is_owner()
	async def unload(self, ctx:commands.Context, extension:str):
		try:
			await self.bot.unload_extension("extensions.bang." + extension)
			await ctx.send(
				content = f"Unloaded: {extension}",
				reference = ctx.message,
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		aliases = ["activity"],
		description = "change the custom status of the bot",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def custom(self, ctx:commands.Context, *, text:str):
		try:
			async with ctx.typing():
				await asyncio.sleep(1)
			embed = self.bot.embed(
				ctx = ctx,
				bot = True,
			)
			embed.add_field(name="Custom", value=text)
			await ctx.send(
				embed = embed,
				reference = ctx.message,
			)
			await self.bot.change_presence(
				activity = discord.CustomActivity(
					type = discord.ActivityType.custom,
					name = text,
				)
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		aliases = ["playing"],
		description = "change the game status of the bot",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def game(self, ctx:commands.Context, *, text:str):
		try:
			async with ctx.typing():
				await asyncio.sleep(1)
			embed = self.bot.embed(
				ctx = ctx,
				bot = True,
			)
			embed.add_field(name="Game", value=text)
			await ctx.send(
				embed = embed,
				reference = ctx.message,
			)
			await self.bot.change_presence(
				activity = discord.Game(
					name = text,
				)
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		aliases = ["competing"],
		description = "change the watch status of the bot",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def compete(self, ctx:commands.Context, *, text:str):
		try:
			async with ctx.typing():
				await asyncio.sleep(1)
			embed = self.bot.embed(
				ctx = ctx,
				bot = True,
			)
			embed.add_field(name="Compete", value=text)
			await ctx.send(
				embed = embed,
				reference = ctx.message,
			)
			await self.bot.change_presence(
				activity = discord.Activity(
					type = discord.ActivityType.competing,
					name = text,
				)
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		aliases = ["watching"],
		description = "change the watch status of the bot",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def watch(self, ctx:commands.Context, *, text:str):
		try:
			async with ctx.typing():
				await asyncio.sleep(1)
			embed = self.bot.embed(
				ctx = ctx,
				bot = True,
			)
			embed.add_field(name="Watch", value=text)
			await ctx.send(
				embed = embed,
				reference = ctx.message,
			)
			await self.bot.change_presence(
				activity = discord.Activity(
					type = discord.ActivityType.watching,
					name = text,
				)
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		aliases = ["listening"],
		description = "change the watch status of the bot",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def listen(self, ctx:commands.Context, *, text:str):
		try:
			async with ctx.typing():
				await asyncio.sleep(1)
			embed = self.bot.embed(
				ctx = ctx,
				bot = True,
			)
			embed.add_field(name="Listen", value=text)
			await ctx.send(
				embed = embed,
				reference = ctx.message,
			)
			await self.bot.change_presence(
				activity = discord.Activity(
					type = discord.ActivityType.listening,
					name = text,
				)
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		aliases = ["streaming"],
		description = "change the watch status of the bot",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def stream(self, ctx:commands.Context, *, text:str):
		try:
			async with ctx.typing():
				await asyncio.sleep(1)
			embed = self.bot.embed(
				ctx = ctx,
				bot = True,
			)
			embed.add_field(name="Stream", value=text)
			await ctx.send(
				embed = embed,
				reference = ctx.message,
			)
			await self.bot.change_presence(
				#activity = ctx.guild.me.activity
				activity = discord.Activity(
					type = discord.ActivityType.streaming,
					name = text,
				)
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		aliases = ["hide"],
		description = "set bot to invisible",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def invisible(self, ctx:commands.Context):
		try:
			async with ctx.typing():
				await asyncio.sleep(1)
			embed = self.bot.embed(
				ctx = ctx,
				bot = True,
			)
			embed.add_field(name="Presence", value="invisible")
			await ctx.send(
				embed = embed,
				reference = ctx.message,
			)
			await self.bot.change_presence(
				activity = ctx.guild.me.activity,
				status = discord.Status.invisible,
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		description = "set bot to idle",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def idle(self, ctx:commands.Context):
		try:
			async with ctx.typing():
				await asyncio.sleep(1)
			embed = self.bot.embed(
				ctx = ctx,
				bot = True,
			)
			embed.add_field(name="Presence", value="idle")
			await ctx.send(
				embed = embed,
				reference = ctx.message,
			)
			await self.bot.change_presence(
				activity = ctx.guild.me.activity,
				status = discord.Status.idle,
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		description = "set bot to online",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def online(self, ctx:commands.Context):
		try:
			async with ctx.typing():
				await asyncio.sleep(1)
			embed = self.bot.embed(
				ctx = ctx,
				bot = True,
			)
			embed.add_field(name="Presence", value="online")
			await ctx.send(
				embed = embed,
				reference = ctx.message,
			)
			await self.bot.change_presence(
				activity = ctx.guild.me.activity,
				status = discord.Status.online,
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		description = "set bot to offline",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def offline(self, ctx:commands.Context):
		try:
			async with ctx.typing():
				await asyncio.sleep(1)
			embed = self.bot.embed(
				ctx = ctx,
				bot = True,
			)
			embed.add_field(name="Presence", value="offline")
			await ctx.send(
				embed = embed,
				reference = ctx.message,
			)
			await self.bot.change_presence(
				activity = ctx.guild.me.activity,
				status = discord.Status.offline,
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		description = "set bot to dnd",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def dnd(self, ctx:commands.Context):
		try:
			async with ctx.typing():
				await asyncio.sleep(1)
			embed = self.bot.embed(
				ctx = ctx,
				bot = True,
			)
			embed.add_field(name="Presence", value="dnd")
			await ctx.send(
				embed = embed,
				reference = ctx.message,
			)
			await self.bot.change_presence(
				activity = ctx.guild.me.activity,
				status = discord.Status.dnd,
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		description = "set bot to afk",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def afk(self, ctx:commands.Context):
		try:
			async with ctx.typing():
				await asyncio.sleep(1)
			embed = self.bot.embed(
				ctx = ctx,
				bot = True,
			)
			embed.add_field(name="Presence", value="afk")
			await ctx.send(
				embed = embed,
				reference = ctx.message,
			)
			await self.bot.change_presence(
				activity = ctx.guild.me.activity,
				status=ctx.guild.me.status,
				afk=True
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)


async def setup(bot:commands.Bot) -> None:
	try:
		await bot.add_cog(
			Systems(
				bot
			)
		)
	except Exception as e:
		raise e

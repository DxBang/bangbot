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
				guild = ctx.guild
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
				guild = ctx.guild
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
				delete_after = 120,
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild
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

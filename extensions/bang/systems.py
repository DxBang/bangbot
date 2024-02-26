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
		except Exception as e:
			raise e

	@commands.command(
		description = "Ping latency of the bot",
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
			await ctx.send(f"Pong: {self.bot.latency * 1000:,.0f}ms")
		except Exception as e:
			await self.bot.error(e, guild=ctx.guild)

	@commands.command(
		description = "Get the bot's uptime",
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
			await ctx.send(f"Uptime: {self.bot.uptime()}")
		except Exception as e:
			await self.bot.error(e, guild=ctx.guild)

async def setup(bot:commands.Bot) -> None:
	try:
		await bot.add_cog(
			Systems(
				bot
			)
		)
	except Exception as e:
		raise e

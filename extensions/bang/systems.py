import aiomysql
import asyncio
import json
import os
import re
import psutil, platform
from datetime import datetime, timezone
try:
	import nvgpu
	from nvgpu.list_gpus import device_statuses
except ImportError:
	nvgpu = None
import discord
from discord.ext import commands

class Systems(commands.Cog, name="Bang Systems"):
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
		usage = "ping",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
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
	@commands.has_permissions(moderate_members=True)
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

	@commands.command(
		description = "CPU & memory usage of bot",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def usage(self, ctx:commands.Context):
		try:
			pid = os.getpid()
			py = psutil.Process(pid)
			now = datetime.now(timezone.utc)
			uptime = self.bot.uptime()
			embed = self.bot.embed(
				ctx=ctx,
				title="Usage",
				bot=True,
			)
			embed.add_field(name="System", value=f"{platform.system()}", inline=True)
			embed.add_field(name=platform.system(), value=f"{platform.release()}")
			embed.add_field(name="Boot", value=f"{datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}", inline=True)
			#embed.add_field(name="\u200b", value="\u200b", inline=True)
			embed.add_field(name="Time", value=f"{now.strftime('%Y-%m-%d %H:%M:%S')}", inline=True)
			#embed.add_field(name="\u200b", value="\u200b", inline=True)
			if platform.system() != "Windows":
				temp = psutil.sensors_temperatures()
				fans = psutil.sensors_fans()
				if "k10temp" in temp:
					embed.add_field(name="CPU Temp", value=f"{temp['k10temp'][0].current}℃", inline=True) # ° ℃
				if "nct6795" in fans:
					embed.add_field(name="CPU Fan", value=f"{fans['nct6795'][1].current} RPM", inline=True)
				embed.add_field(name="CPU Usage", value=f"{psutil.cpu_percent()}%", inline=True)
				if "nouveau" in temp and "nouveau" in fans:
					embed.add_field(name="GPU Temp", value=f"{temp['nouveau'][0].current}℃", inline=True) # ° ℃
					embed.add_field(name="GPU Fan", value=f"{fans['nouveau'][0].current} RPM", inline=True)
					#embed.add_field(name="\u200b", value="\u200b", inline=True)
				else:
					if nvgpu is not None:
						gpus = nvgpu.gpu_info()
						infos = device_statuses()
						for gpu in gpus:
							info = infos[int(gpu["index"])]
							embed.add_field(name=f"GPU", value=f"{gpu['type']}", inline=True)
							embed.add_field(name=f"GPU Temp", value=f"{info['temperature']}℃", inline=True)
							embed.add_field(name=f"GPU Clock", value=f"{info['clock_mhz']}Mhz", inline=True)
							embed.add_field(name=f"GPU RAM Usage", value=f"{self.bot.datasize(gpu['mem_used'] * 1024 * 1024)}/{self.bot.datasize(gpu['mem_total'] * 1024 * 1024)}", inline=True)
							#embed.add_field(name="\u200b", value="\u200b", inline=True)
							#embed.add_field(name="\u200b", value="\u200b", inline=True)
				i = 0
				if "nct6795" in fans:
					for v in fans["nct6795"]:
						if i < 2:
							i += 1
							continue
						k = i - 1
						#key = (f'Case Fan #{k}', f'{v.label} Fan')[len(v.label) > 0] # use labeled fan names if exists
						embed.add_field(name=f"Case Fan #{k}", value=f"{v.current} RPM", inline=True)
						i += 1
			#embed.add_field(name="\u200b", value="\u200b", inline=True)
			#embed.add_field(name="\u200b", value="\u200b", inline=True)
			embed.add_field(name="RAM Usage", value=f"{self.bot.datasize(psutil.virtual_memory()[3])}/{self.bot.datasize(psutil.virtual_memory()[0])}", inline=True)
			"""
			await ctx.send(
				embed=embed,
				reference=ctx.message,
				delete_after=3600,
			)
			embed = self.bot.embed(
				ctx=ctx,
				title='Bot Info',
				bot=True,
			)
			"""
			embed.add_field(name="BangBot", value=f"{self.bot.__version__}")
			embed.add_field(name="Discord.py", value=f"{discord.__version__}")
			embed.add_field(name="Python", value=f"{platform.python_version()}")
			#embed.add_field(name="\u200b", value="\u200b", inline=True)
			#embed.add_field(name="\u200b", value="\u200b", inline=True)
			#embed.add_field(name=f"Bot PID", value=f"{pid}", inline=True)
			embed.add_field(name="Uptime", value=f"{uptime}")
			#embed.add_field(name="\u200b", value="\u200b", inline=True)
			embed.add_field(name=f"Bot CPU Usage", value=f"{py.cpu_percent()}%", inline=True)
			embed.add_field(name=f"Bot RAM Usage", value=f"{self.bot.datasize(py.memory_info()[0])}", inline=True)
			#embed.add_field(name="Links", value="[Hilda](https://clare3dx.com/gallery/tagged/hilda)", inline=False)
			#embed.set_footer(text="[3DX.World](https://3dx.world)")
			return await ctx.send(
				embed=embed,
				reference=ctx.message,
			)
		except Exception as e:
			await self.bot.error(e, guild=ctx.guild)


	@commands.command(
		description = "Sync the bot's slash commands",
		hidden = True,
	)
	@commands.guild_only()
	@commands.is_owner()
	@commands.has_permissions(moderate_members=True)
	async def sync(self, ctx:commands.Context) -> None:
		try:
			synced = await self.bot.tree.sync(
				guild = ctx.guild
			)
			await ctx.send(
				f"Synced: {len(synced)} commands"
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		description = "Load an extension",
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
		description = "Reload an extension",
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
		description = "Unload an extension",
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
		description = "Change the custom status of the bot",
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
		description = "Change the game status of the bot",
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
		description = "Change the watch status of the bot",
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
		description = "Change the watch status of the bot",
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
		description = "Change the watch status of the bot",
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
		description = "Change the watch status of the bot",
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
		description = "Set bot to invisible",
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
		description = "Set bot to idle",
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
		description = "Set bot to online",
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
		description = "Set bot to offline",
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
		description = "Set bot to dnd",
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
		description = "Set bot to afk",
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
				status = ctx.guild.me.status,
				afk = True
			)
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)

	@commands.command(
		description = "Chat in a channel as the bot",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def chat(self, ctx:commands.Context, channel:discord.TextChannel, *, text:str):
		try:
			# check if the bot has permission to send messages in the channel
			if not channel.permissions_for(ctx.guild.me).send_messages:
				return await ctx.send(
					content = f"I don't have permission to send messages in {channel.mention}",
					reference = ctx.message,
				)
			async with channel.typing():
				await asyncio.sleep(1)
			files = None
			if len(ctx.message.attachments) > 0:
				files = await self.bot.download_attachments(ctx.message.attachments)
			await channel.send(
				content = text,
				files = files,
			)
			await ctx.message.delete()
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

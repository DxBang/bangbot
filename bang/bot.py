import os, sys
from genericpath import exists
import traceback
import json
import random
import discord
import tempfile
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta, timezone
from typing import Coroutine, NamedTuple

def cprint(message:str, fg:str="white", bg:str="black", end:str="\n") -> None:
	fg:int = {
		"black": 30,
		"red": 31,
		"green": 32,
		"orange": 33,
		"blue": 34,
		"magenta": 35,
		"purple": 35,
		"cyan": 36,
		"white": 37,
		"gray": 90,
		"bright_red": 91,
		"pink": 91,
		"bright_green": 92,
		"yellow": 93,
		"bright_blue": 94,
		"bright_magenta": 95,
		"bright_purple": 95,
		"bright_cyan": 96,
	}.get(fg, 37)
	bg:int = {
		"black": 40,
		"red": 41,
		"green": 42,
		"orange": 43,
		"blue": 44,
		"magenta": 45,
		"purple": 45,
		"cyan": 46,
		"white": 47,
		"gray": 100,
		"bright_red": 101,
		"pink": 101,
		"bright_green": 102,
		"yellow": 103,
		"bright_blue": 104,
		"bright_magenta": 105,
		"bright_purple": 105,
		"bright_cyan": 106,
		"bright_white": 107,
	}.get(bg, 40)
	print(f"\033[1;{fg};{bg}m{message}\033[0m", end=end)



class Bang(commands.Bot):
	__slots__ = (
		"token",
		"config",
		"data",
		"sql",
		"console",
		"__POWERED_BY__",
		"__version__",
	)

	def __init__(self, token:str = None) -> None:
		try:
			if token is None:
				raise ValueError("Token is not provided.")
			self.token = token
			with open('.version', 'r') as f:
				self.__version__ = f.read().strip()
			# print in white
			cprint(f"BangBot v{self.__version__} (discord.py v{discord.__version__}) (Python v{sys.version.split(' ')[0]})", "blue")
			print("Loading config.json")
			self.__POWERED_BY__ = "Bang Systems"
			with open(sys.path[0] + "/config.json", encoding="utf-8") as f:
				self.config = json.load(f)
			self.config.update(
				{
					"guilds": {}
				}
			)
			self.data = {
				"service": datetime.now(timezone.utc),
				"connect": None,
			}
			with open(sys.path[0] + "/guild/_default_.json", encoding="utf-8") as f:
				self.config["default"] = json.load(f)
			intents = discord.Intents.all()
			super().__init__(
				command_prefix = commands.when_mentioned_or(*self.config["bot"]["prefix"]),
				intents = intents,
				case_insensitive = True,
				guild_subscriptions = True,
				fetch_offline_members = True,
				chunk_guilds_at_startup = True,
				max_messages = 2000,
				status = self.config["bot"]["activity"]["status"],
				activity = discord.Activity(
					name = self.config["bot"]["activity"]["message"],
					type = getattr(discord.ActivityType, self.config["bot"]["activity"]["type"]),
				)
			)
			self.sql = None
		except FileNotFoundError:
			cprint("json not found.", "red")
			sys.exit(1)
		except json.JSONDecodeError:
			cprint("invalid json file.", "red")
			sys.exit(1)
		except Exception as e:
			traceback.print_exc()
			sys.exit(1)

	def run(self) -> None:
		try:
			cprint("run()", "green")
			super().run(
				self.token,
				reconnect = True
			)
		except discord.LoginFailure:
			cprint("Invalid token.", "red")
			sys.exit(1)
		except discord.HTTPException:
			cprint("Failed to connect to Discord.", "red")
			sys.exit(1)
		except Exception as e:
			traceback.print_exc()
			sys.exit(1)

	async def setup_hook(self) -> None:
		try:
			cprint("setup_hook()", "green")
			print(f"Temp: {self.get_temp()}")
			for ext in self.config["extensions"]:
				if ext[0] == "!":
					continue
				print(f"Loading {ext}")
				await self.load_extension(
					"extensions." + ext
				)
		except discord.HTTPException:
			cprint("Failed to load extension.", "red")
			sys.exit(1)
		except Exception as e:
			traceback.print_exc()
			sys.exit(1)

	async def on_connect(self) -> None:
		try:
			cprint("on_connect()", "green")
			self.data.update(
				{
					"connect": datetime.now(timezone.utc)
				}
			)
			print(f"Connected to Discord at {self.data['connect']}")
		except Exception as e:
			traceback.print_exc()
			sys.exit(1)

	async def on_ready(self) -> None:
		try:
			cprint("on_ready()", "green")
			cprint(f"Logged in as {self.user.name} ({self.user.id})", "black", "white")
			# await self.setup_hook()
			await self.wait_until_ready()
			for guild in self.guilds:
				await self.sync(
					guild
				)
			return
		except Exception as e:
			traceback.print_exc()
			sys.exit(1)

	async def sync(self, guild:discord.Guild = None) -> list:
		try:
			cprint(f"sync({guild})", "green")
			if guild is None:
				raise ValueError("Guild is not provided.")
			cprint(f"sync: {guild.name} ({guild.id})", "cyan")
			# sync app commands / slash commands
			sync = await self.tree.sync(guild = guild)
			cprint(f"	synced {len(sync)} command(s).", "cyan")
			return sync
		except Exception as e:
			traceback.print_exc()
			raise e

	async def on_resumed(self) -> None:
		try:
			cprint(f"on_resumed()", "green")
		except Exception as e:
			await self.error(
				e
			)

	async def on_guild_join(self, guild:discord.Guild) -> None:
		try:
			cprint(f"on_guild_join({guild})", "green")
		except Exception as e:
			await self.error(
				e,
				guild = guild
			)

	async def on_guild_remove(self, guild:discord.Guild) -> None:
		try:
			cprint(f"on_guild_remove({guild})", "green")
		except Exception as e:
			await self.error(
				e,
				guild = guild
			)

	async def on_guild_unavailable(self, guild:discord.Guild) -> None:
		try:
			cprint(f"on_guild_unavailable({guild})", "green")
		except Exception as e:
			await self.error(
				e,
				guild = guild
			)

	async def on_shard_ready(self, shard_id:int) -> None:
		try:
			cprint(f"on_shard_ready({shard_id})", "green")
		except Exception as e:
			await self.error(
				e
			)

	async def on_shard_connect(self, shard_id:int) -> None:
		try:
			cprint(f"on_shard_connect({shard_id})", "green")
		except Exception as e:
			await self.error(
				e
			)

	async def on_shard_disconnect(self, shard_id:int) -> None:
		try:
			cprint(f"on_shard_disconnect({shard_id})", "green")
		except Exception as e:
			await self.error(
				e
			)

	async def on_shard_resumed(self, shard_id:int) -> None:
		try:
			cprint(f"on_shard_resumed({shard_id})", "green")
		except Exception as e:
			await self.error(
				e
			)

	async def on_guild_available(self, guild:discord.Guild) -> None:
		try:
			cprint(f"on_guild_available({guild})", "green")
			config_file = sys.path[0] + "/guild/" + str(guild.id) + ".json"
			if exists(config_file):
				with open(config_file, encoding="utf-8") as fh:
					config = json.loads(
						fh.read(),
					)
					config["id"] = guild.id
					self.config["guilds"].update({guild.id: config})
				nick = self.get_config(guild, "nick")
				if nick is not None:
					await guild.me.edit(
						nick=nick
					)
				cprint(f"nick: {guild.me.nick}", "blue")
		except Exception as e:
			await self.error(
				e,
				guild = guild
			)

	def main_guild(self):
		try:
			return self.get_guild(
				self.config["default"]["main"]
			)
		except Exception as e:
			self.warn(e)

	def get_default(self, *args) -> list | dict | int | str | bool | None:
		try:
			config = self.config["default"]
			for arg in args:
				if arg in config:
					config = config[arg]
					continue
				config = None
				break
			return config
		except Exception as e:
			self.warn(e)

	def get_config(self, guild:discord.Guild = None, *args) -> list | dict | int | str | bool | None:
		try:
			found:bool = False
			if guild is not None and guild.id in self.config["guilds"]:
				config = self.config["guilds"][guild.id]
				found = True
				for arg in args:
					if arg in config:
						config = config[arg]
						continue
					config = None
					found = False
					break
			if found:
				return config
			return self.get_default(*args)
		except Exception as e:
			self.warn(e)

	def get_temp(self) -> str:
		try:
			use_system_temp = self.config["bot"]["use_system_temp"]
			if use_system_temp is not None and use_system_temp is True:
				return tempfile.gettempdir()
			return os.path.join(
				sys.path[0],
				"tmp"
			)
			#return tempfile.gettempdir()
		except Exception as e:
			self.warn(e)

	def uptime(self) -> str:
		try:
			delta = datetime.now(timezone.utc) - self.data["service"]
			return str(delta).split(".")[0]
		except Exception as e:
			self.warn(e)

	def datasize(self, bytes:int) -> str:
		try:
			if bytes < 1024:
				return f"{bytes} B"
			if bytes < 1048576:
				return f"{bytes / 1024:.2f} KB"
			if bytes < 1073741824:
				return f"{bytes / 1048576:.2f} MB"
			return f"{bytes / 1073741824:.2f} GB"
		except Exception as e:
			self.warn(e)


	def embed(self,
			ctx:commands.Context,
			# message:discord.Message = None,
			guild:discord.Guild = None,
			member:discord.Member = None,
			title:str = None,
			description:str = None,
			bot:bool = False,
			author:bool = False,
			thumbnail:bool = False,
			color:str = None,
		) -> discord.Embed:
		try:
			#if ctx is not None and message is None:
			#	message = ctx
			if ctx is not None and guild is None:
				guild = ctx.guild
			if ctx is not None and member is None:
				member = ctx.author
			if color is None:
				if author is True:
					color = ctx.author.color
				elif bot is True:
					color = ctx.me.color
				else:
					color = discord.Color.blue()
			embed = discord.Embed(
				title = title,
				description = description,
				color = color,
			)
			if author and self.get_config(guild, "embed", "author"):
				if bot:
					embed.set_author(
						name = guild.me.name,
						icon_url = guild.me.avatar,
					)
				else:
					embed.set_author(
						name = member.display_name,
						icon_url = member.avatar,
					)
			if thumbnail and self.get_config(guild, "embed", "thumbnail"):
				if bot:
					embed.set_thumbnail(
						url = guild.me.avatar,
					)
				if author:
					embed.set_thumbnail(
						url = member.avatar,
					)
				else:
					embed.set_thumbnail(
						url = guild.icon,
					)
			if self.get_config(guild, "embed", "footer"):
				embed.set_footer(
					text = guild.name,
				)
			return embed
		except Exception as e:
			self.warn(
				e
			)

	async def download_attachment(self, attachment:discord.Attachment) -> discord.File:
		try:
			path = os.path.join(
				self.get_temp(),
				attachment.filename
			)
			await attachment.save(
				path
			)
			return discord.File(
				path,
				filename=attachment.filename
			)
		except Exception as e:
			self.warn(
				e,
			)

	async def download_attachments(self, attachments:list) -> list:
		try:
			# use discord.file()
			files = []
			for attachment in attachments:
				files.append(
					await self.download_attachment(attachment)
				)
			return files
		except Exception as e:
			self.warn(
				e
			)

	# errors
	async def error(
			self,
			error:str,
			guild:discord.Guild = None,
			message:discord.Message = None,
		) -> None:
		frame = sys._getframe(1)
		section = f"{frame.f_locals['self'].__class__.__name__}/{frame.f_code.co_name}"
		print(f"\033[1;31mERROR: {section}: {error}\033[0m")
		traceback.print_exc()
		trace = traceback.format_exc()
		if guild is None:
			guild = self.main_guild()
		await self.log(
			guild = guild,
			log = f"{section}/error: {error}\n"\
				f"```{trace[:1000]}```",
			message = message,
		)

	def warn(
			self,
			warn:str,
		) -> None:
		frame = sys._getframe(1)
		section = f"{frame.f_locals['self'].__class__.__name__}/{frame.f_code.co_name}"
		trace = traceback.format_exc()
		print(f"\033[1;31mERROR: {section}: {warn}\033[0m")
		print(f"TRACE:\n{trace}")

	# log
	async def log(self,
			guild:discord.Guild = None,
			log:str = None,
			message:discord.Message = None,
			files:list = None
		) -> None:
		try:
			return
			print(f"LOG: {guild}: {log}")
			if guild is None:
				guild = self.main_guild()
			if log is None:
				log = self.datetime(datetime.now(timezone.utc))
			channel = self.get_config(guild, "channel", "log")
			if channel is None:
				return
			channel = self.get_channel(channel)
			if channel is None:
				return
			embed = self.embed(
				ctx = channel,
				guild = guild,
				member = guild.me,
				title = f"{__class__.__name__}.{sys._getframe(1).f_code.co_name}",
				description = log,
				bot = True,
				thumbnail = False,
				author = False,
			)
			if message is not None:
				embed.add_field(
					name = "Channel",
					value = message.channel.mention,
					inline = True,
				)
				embed.add_field(
					name = "Author",
					value = message.author.mention,
					inline = True,
				)
				embed.add_field(
					name = "Created",
					value = self.datetime(message.created_at),
					inline = True,
				)
				embed.add_field(
					name = "Message",
					value = message.content,
					inline = False,
				)
			if not files:
				return await channel.send(
					embed = embed
				)
			uploads = []
			filenames = []
			if files is not None:
				for file in files:
					filenames.append(
						file["name"]
					)
					uploads.append(
						discord.File(
							file["path"],
							filename=file["name"]
						)
					)
			await channel.send(
				embed = embed,
				files = uploads,
			)
			if files is not None:
				for file in files:
					os.unlink(file["path"])
		except Exception as e:
			print(f"{__class__.__name__}/{sys._getframe(0).f_code.co_name}/error: {e}")
			traceback.print_exc()

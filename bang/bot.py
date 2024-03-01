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

	def __init__(self, token:str = None, version:str = None) -> None:
		try:
			if token is None:
				raise ValueError("Token is not provided.")
			if version is None:
				raise ValueError("Token is not provided.")
			self.token = token
			print("Loading config.json")
			self.__POWERED_BY__ = "Bang Systems"
			self.__version__ = version
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
			print("json not found.")
			sys.exit(1)
		except json.JSONDecodeError:
			print("invalid json file.")
			sys.exit(1)
		except Exception as e:
			traceback.print_exc()
			sys.exit(1)

	def run(self) -> None:
		try:
			super().run(
				self.token,
				reconnect = True
			)
		except discord.LoginFailure:
			print("Invalid token.")
			sys.exit(1)
		except discord.HTTPException:
			print("Failed to connect to Discord.")
			sys.exit(1)
		except Exception as e:
			traceback.print_exc()
			sys.exit(1)

	async def setup_hook(self) -> None:
		try:
			for ext in self.config["extensions"]:
				if ext[0] == "!":
					continue
				print(f"Loading {ext}")
				await self.load_extension(
					"extensions." + ext
				)
		except discord.HTTPException:
			print("Failed to load extension.")
			sys.exit(1)
		except Exception as e:
			traceback.print_exc()
			sys.exit(1)

	async def on_connect(self) -> None:
		try:
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
			print(f"Logged in as {self.user.name} ({self.user.id})")
			# await self.setup_hook()
		except Exception as e:
			traceback.print_exc()
			sys.exit(1)

	async def on_guild_available(self, guild:discord.Guild) -> None:
		try:
			print(f"  GUILD: {guild.name} ({guild.id})")
			config_file = sys.path[0] + "/guild/" + str(guild.id) + ".json"
			if exists(config_file):
				with open(config_file, encoding="utf-8") as fh:
					config = json.loads(
						fh.read(),
					)
					config["id"] = guild.id
					self.config["guilds"].update({guild.id: config})
				print(f"   CONFIG: {config}")
				nick = self.get_config(guild, "nick")
				if nick is not None:
					await guild.me.edit(
						nick=nick
					)
				print(f"   NICK: {guild.me.nick}")
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
			self.warn(e)

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
			await self.error(
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
			await self.error(
				e,
				guild = message.guild
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
			error:str,
		) -> None:
		frame = sys._getframe(1)
		section = f"{frame.f_locals['self'].__class__.__name__}/{frame.f_code.co_name}"
		trace = traceback.format_exc()
		print(f"\033[1;31mERROR: {section}: {error}\033[0m")
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

import sys
from genericpath import exists
import traceback
import json
import random
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta, timezone
from typing import Coroutine, NamedTuple
import platform
from .dest import Dest


def cprint(message:str, fg:str="white", bg:str="black", end:str="\n") -> None:
	fg:int = {
		"black": 30,
		"red": 31,
		"green": 32,
		"orange": 33,
		"yellow": 33,
		"blue": 34,
		"magenta": 35,
		"purple": 35,
		"cyan": 36,
		"white": 37,
		"gray": 90,
		"bright_red": 91,
		"pink": 91,
		"bright_green": 92,
		"bright_yellow": 93,
		"bright_blue": 94,
		"bright_magenta": 95,
		"bright_purple": 95,
		"bright_cyan": 96,
		"bright_white": 97,

	}.get(fg, 37)
	bg:int = {
		"black": 40,
		"red": 41,
		"green": 42,
		"orange": 43,
		"yellow": 43,
		"blue": 44,
		"magenta": 45,
		"purple": 45,
		"cyan": 46,
		"white": 47,
		"dark_gray": 100,
		"gray": 100,
		"bright_red": 101,
		"pink": 101,
		"bright_green": 102,
		"bright_yellow": 103,
		"bright_blue": 104,
		"bright_magenta": 105,
		"bright_purple": 105,
		"bright_cyan": 106,
		"bright_white": 107,
	}.get(bg, 40)
	print(f"\033[1;{fg};{bg}m{message}\033[0m", end=end)



class Bot(commands.Bot):
	__slots__ = (
		"token",
		"config",
		"data",
		"sql",
		"console",
		"__name__",
		"__version__",
		"__POWERED_BY__",
	)
	def test(self):
		print("tested!")

	def __init__(self, token:str = None) -> None:
		try:
			if token is None:
				raise ValueError("Token is not provided.")
			self.token = token
			self.__name__ = "BangBot"
			with open('.version', 'r') as f:
				self.__version__ = f.read().strip()
			self.__POWERED_BY__ = "Powered by Bang Systems"
			# print in white
			cprint(f"{self.__name__} v{self.__version__} (discord.py v{discord.__version__}) (Python v{platform.python_version()})", "blue")
			print("Loading config.json")
			self.config = Dest.json.load(Dest.file("config.json"))
			self.config.update(
				{
					"guilds": {}
				}
			)
			self.data = {
				"service": datetime.now(timezone.utc),
				"connect": None,
			}
			self.config["default"] = Dest.json.load(Dest.file("guild/_default_.json"))
			intents = discord.Intents.all()
			activity = self.setActivity(
				self.config["bot"]["activity"]['type'],
				self.config["bot"]["activity"]['message'],
				extra = dict(
					start = self.data["service"],
					url = 'https://bang.systems/',
				)
			)
			super().__init__(
				command_prefix = commands.when_mentioned_or(*self.config["bot"]["prefix"]),
				intents = intents,
				case_insensitive = True,
				guild_subscriptions = True,
				fetch_offline_members = True,
				chunk_guilds_at_startup = True,
				max_messages = 2000,
				status = self.config["bot"]["activity"]["status"],
				activity = activity
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

	def setActivity(self, type:str, message:str, extra:dict = None) -> discord.Activity | discord.Game | discord.Streaming | discord.Activity | discord.CustomActivity | None:
		try:
			if type == "playing":
				return discord.Game(
					name = message,
					start = extra['start'] if 'start' in extra is not None else None,
					end = extra['end'] if 'end' in extra is not None else None,
				)
			if type == "streaming":
				return discord.Streaming(
					name = message,
					url = extra['url'] if 'url' in extra is not None else None,
				)
			if type == "listening":
				return discord.Activity(
					name = message,
					type = discord.ActivityType.listening
				)
			if type == "watching":
				return discord.Activity(
					name = message,
					type = discord.ActivityType.watching
				)
			if type == "competing":
				return discord.Activity(
					name = message,
					type = discord.ActivityType.competing
				)
			if type == "custom":
				return discord.CustomActivity(
					name = message,
					type = discord.ActivityType.custom,
				)
			return discord.Activity(
				name = message,
				type = discord.ActivityType.playing
			)
		except Exception as e:
			traceback.print_exc()
			raise e

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
			print(f"Temp: {self.getTemp()}")
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
			await self.sync()
			#for guild in self.guilds:
			#	await self.sync(
			#		guild
			#	)
			print(f"Ready to serve {len(self.guilds)} guild(s).")
		except Exception as e:
			traceback.print_exc()
			sys.exit(1)

	async def sync(self, guild:discord.Guild = None) -> list:
		try:
			cprint(f"sync({guild})", "green")
			if guild is None:
				synced = await self.tree.sync()
			else:
				cprint(f"sync: {guild.name} ({guild.id})", "cyan")
				# sync app commands / slash commands
				self.tree.copy_global_to(guild=guild)
				synced = await self.tree.sync(guild=guild)
			for command in synced:
				cprint(f"/{command}", "cyan")
			cprint(f"Synced a total of {len(synced)} command(s).", "cyan")
			return synced
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
			config_file = Dest.file(f"guild/{str(guild.id)}.json")
			if Dest.exists(config_file):
				config = Dest.json.load(config_file)
				save = False
				if "id" not in config:
					config["id"] = guild.id
					save = True
				if "name" not in config:
					config["name"] = guild.name
					save = True
				if save:
					Dest.json.save(config_file, config)
				self.config["guilds"].update({guild.id: config})
				nick = self.getConfig(guild, "nick")
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
			self.debug(e)

	def getDefault(self, *args) -> list | dict | int | str | bool | None:
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
			self.debug(e)

	def getConfig(self, guild:discord.Guild = None, *args) -> list | dict | int | str | bool | None:
		try:
			default = self.getDefault(*args)
			if guild is None:
				return default
			if guild.id in self.config["guilds"]:
				# look through the guild's config from the args and merge it with the default config if it exists in the guild's config and the default config
				config = self.config["guilds"][guild.id]
				for arg in args:
					if arg in config:
						config = config[arg]
						continue
					config = None
					break
				if config is not None:
					# merge the default config with the guild's config
					if isinstance(config, dict) and isinstance(default, dict):
						default.update(config)
						return default
					if isinstance(config, list) and isinstance(default, list):
						default.extend(config)
						return default
					return config
			return default
		except Exception as e:
			self.debug(e)

	def getTemp(self, subfolder:str = None, guild:discord.Guild = None) -> str:
		try:
			if subfolder is not None and guild is not None:
				subfolder = f"{guild.id}/{subfolder}"
			elif subfolder is None and guild is not None:
				subfolder = f"{guild.id}"
			return Dest.temp(
				system = self.config["bot"]["use_system_temp"],
				subfolder = subfolder
			)
		except Exception as e:
			self.debug(e)

	def uptime(self) -> str:
		try:
			delta = datetime.now(timezone.utc) - self.data["service"]
			return str(delta).split(".")[0]
		except Exception as e:
			self.debug(e)

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
			self.debug(e)

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
			if author and self.getConfig(guild, "embed", "author"):
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
			if thumbnail and self.getConfig(guild, "embed", "thumbnail"):
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
			if self.getConfig(guild, "embed", "footer"):
				embed.set_footer(
					text = guild.name,
				)
			return embed
		except Exception as e:
			self.debug(
				e
			)

	async def downloadAttachment(self, attachment:discord.Attachment, subfolder:str = None) -> discord.File:
		try:
			temp = self.getTemp(subfolder)
			path = Dest.join(
				temp,
				attachment.filename
			)
			await attachment.save(
				fp = path
			)
			return discord.File(
				fp = path,
				filename = attachment.filename
			)
		except Exception as e:
			self.debug(
				e,
			)

	async def downloadAttachments(self, attachments:list, subfolder:str = None) -> list:
		try:
			# use discord.file()
			files = []
			for attachment in attachments:
				files.append(
					await self.downloadAttachment(attachment, subfolder)
				)
			return files
		except Exception as e:
			self.debug(
				e
			)

	# errors
	async def error(
			self,
			error:str,
			ctx:commands.Context,
		) -> None:
		frame = sys._getframe(1)
		section = f"{frame.f_locals['self'].__class__.__name__}/{frame.f_code.co_name}"
		cprint(message=f"ERROR: {section}: {error}", fg="red", bg="black")
		trace = traceback.format_exc()
		await ctx.send(
			content = f"**Error:** {error}",
			reference = ctx.message,
			delete_after = 60,
		)
		await self.log(
			ctx = ctx,
			log = f"{section}/error: {error}\n"\
				f"```{trace[:1000]}```"
		)

	async def warn(
			self,
			warn:str,
			ctx:commands.Context,
		) -> None:
		frame = sys._getframe(1)
		section = f"{frame.f_locals['self'].__class__.__name__}/{frame.f_code.co_name}"
		cprint(message=f"WARNING: {section}: {warn}", fg="yellow", bg="black")
		await ctx.send(
			content = f"**Warning:** {warn}",
			reference = ctx.message,
			delete_after = 60,
		)

	async def log(self,
			log:str,
			ctx:commands.Context,
		) -> None:
		try:
			cprint(f"LOG: {ctx.guild}: {log}", fg="cyan", bg="black")
			message = ctx.message
			log_channel = self.getConfig(ctx.guild, "channel", "log")
			if log_channel is None:
				return
			log_channel = self.get_channel(log_channel)
			embed = self.embed(
				ctx = ctx,
				title = f"{__class__.__name__}.{sys._getframe(1).f_code.co_name}",
				description = log,
				bot = True,
			)
			if message is not None:
				if message.channel.type == discord.ChannelType.private:
					embed.add_field(
						name = "Channel",
						value = "Private",
						inline = True,
					)
				elif message.channel.type == discord.ChannelType.text:
					embed.add_field(
						name = "Channel",
						value = message.jump_url,
						inline = True,
					)
				embed.add_field(
					name = "Author",
					value = message.author.mention,
					inline = True,
				)
				embed.add_field(
					name = "Message",
					value = message.content,
					inline = False,
				)
				files = None
				if len(message.attachments) > 0:
					files = await self.downloadAttachments(message.attachments, "log")
					embed.add_field(
						name = "Attachments",
						value = "\n".join([file.filename for file in files]),
						inline = False,
					)
			await log_channel.send(
				embed = embed,
				files = files,
			)
			if isinstance(files, list) and len(files) > 0:
				for file in files:
					file.close()
					Dest.remove(file.fp.name)
		except Exception as e:
			cprint(
				message = f"{__class__.__name__}/{sys._getframe(0).f_code.co_name}/error: {e}",
				fg = "red",
				bg = "white"
			)
			traceback.print_exc()

	def debug(
			self,
			debug:str,
		) -> None:
		frame = sys._getframe(1)
		section = f"{frame.f_locals['self'].__class__.__name__}/{frame.f_code.co_name}"
		cprint(message=f"DEBUG: {section}: {debug}", fg="bright_magenta", bg="gray")
		traceback.print_exc()

	@commands.Cog.listener()
	async def on_command_error(self, ctx:commands.Context, error:commands.CommandError) -> None:
		try:
			if hasattr(ctx.cog, f"_{ctx.cog.__class__.__name__}__error"):
				return
			if hasattr(ctx.command, "on_error"):
				return
			error = getattr(error, "original", error)
			if isinstance(error, (
					commands.CommandNotFound,
					#commands.UserInputError
				)):
				return
			if isinstance(error, commands.CommandOnCooldown):
				now = datetime.now(timezone.utc)
				cooldown = (now + timedelta(seconds=round(error.retry_after))) - now
				return await ctx.send(
					random.choice(
						self.getConfig(ctx.guild, "response", "error_command_cooldown")
					).format(
						author = ctx.author.mention,
						command = ctx.command,
						cooldown = cooldown,
						type = error.type,
					),
					reference=ctx.message,
					delete_after=300,
				)
			elif isinstance(error, commands.DisabledCommand):
				return await ctx.send(
					random.choice(
						self.getConfig(ctx.guild, "response", "error_command_disabled")
					).format(
						author = ctx.author.mention,
						command = ctx.command,
					),
					reference = ctx.message,
					delete_after = 300,
				)
			elif isinstance(error, commands.MissingRequiredArgument):
				return await ctx.send(
					random.choice(
						self.getConfig(ctx.guild, "response", "error_command_missing_argument")
					).format(
						author = ctx.author.mention,
						command = ctx.command,
						param = error.param,
					),
					reference = ctx.message,
					delete_after = 300,
				)
			elif isinstance(error, commands.CommandNotFound):
				return await ctx.send(
					random.choice(
						self.getConfig(ctx.guild, "response", "error_command_not_found")
					).format(
						author = ctx.author.mention,
						command = ctx.command,
					),
					reference = ctx.message,
					delete_after = 300,
				)

			elif isinstance(error, commands.NoPrivateMessage):
				try:
					return await ctx.author.send(
						random.choice(
							self.getConfig(ctx.guild, "response", "error_command_not_in_private")
						).format(
							author = ctx.author.mention,
							command = ctx.command,
						)
					)
				except:
					pass
			elif isinstance(error, commands.BadArgument):
				if ctx.command.qualified_name == "tag list":
					return await ctx.send(
						random.choice(
							self.getConfig(ctx.guild, "response", "error_command_bad_argument_tag")
						).format(
							author = ctx.author.mention,
							command = ctx.command,
							args = error.args
						),
						reference = ctx.message,
						delete_after = 300,
					)
				return await ctx.send(
					random.choice(
						self.getConfig(ctx.guild, "response", "error_command_bad_argument")
					).format(
						author = ctx.author.mention,
						command = ctx.command,
						args = error.args
					),
					reference = ctx.message,
					delete_after = 300,
				)
			elif isinstance(error, commands.NotOwner):
				return await ctx.send(
					random.choice(
						self.getConfig(ctx.guild, "response", "error_command_not_owner")
					).format(
						author = ctx.author.mention,
						command = ctx.command,
						args = error.args
					),
					reference = ctx.message,
					delete_after = 300,
				)
			elif isinstance(error, commands.MissingPermissions):
				return await ctx.send(
					random.choice(
						self.getConfig(ctx.guild, "response", "error_command_missing_permissions")
					).format(
						author = ctx.author.mention,
						command = ctx.command,
						args = error.args
					),
					reference = ctx.message,
					delete_after = 300,
				)
			else:
				print(f"{error} type {type(error)}")
				await ctx.send(
					error,
					reference = ctx.message,
					delete_after = 300,
				)
			if ctx.command is None:
				raise Exception(f"{__class__.__name__}/error: {error} // type {type(error)}")
			raise Exception(f"{__class__.__name__}/{ctx.command}/error: {error} // type {type(error)}")
		except Exception as e:
			await self.error(
				error = e,
				ctx = ctx,
			)

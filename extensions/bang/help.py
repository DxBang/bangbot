import discord
from discord.ext import commands
from discord import app_commands
import traceback
import re

class Help(commands.Cog, name="Help Command"):
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
		description = "Show this help...",
		usage = "help [command/cog/extension]",
		aliases = [
			"h",
		],
	)
	async def help(self, ctx:commands.Context, help:str = None) -> None:
		try:
			if help is not None:
				help = help.lower()
				# get the command
				command = self.bot.get_command(help)
				if command is None:
					# get app command for the cogs
					for cog in self.bot.cogs:
						commands = self.bot.cogs[cog].get_app_commands()
						if len(commands) > 0:
							for command in commands:
								if command.name == help:
									print(f"command: {command}")
									break
				if command is None:
					embed = self.bot.embed(
						ctx = ctx,
						title = "Help",
						description = "Command not found",
						bot = True,
					)
					embed.set_footer(
						text = f"Powered by {self.bot.__POWERED_BY__}",
					)
					return await ctx.send(
						embed=embed
					)
				embed = self.bot.embed(
					ctx = ctx,
					title = f"Help: {command.name}",
					description = command.description,
					bot = True,
				)
				if hasattr(command, 'aliases') and command.aliases:
					embed.add_field(
						name = "Aliases",
						value = ", ".join(command.aliases),
						inline = False,
					)
				if hasattr(command, 'usage') and command.usage:
					embed.add_field(
						name = "Usage",
						value = f"{ctx.prefix}{command.usage}",
						inline = False,
					)
				# replace {ctx.prefix} with the actual prefix

				if hasattr(command, 'help') and command.help:
					embed.add_field(
						name = "Help",
						value = re.sub(r"{ctx.prefix}", ctx.prefix, command.help),
						inline = False,
					)
				if hasattr(command, 'hidden'):
					if command.hidden:
						embed.add_field(
							name = "Hidden",
							value = "Yes",
							inline = False,
						)
			if help is None:
				embed = self.bot.embed(
					ctx = ctx,
					title = "Help",
					description = "List of commands and cogs",
					bot = True,
				)
				# list of cogs
				cogs = self.bot.cogs
				showHiddenChannels = self.bot.get_config(ctx.guild, "channel", "staff")
				# format showHiddenChannels = [channel.id, channel.id, channel.id]
				showHidden = False
				if showHiddenChannels:
					# check if current channel is in the list of hidden channels
					showHidden = ctx.channel.id in showHiddenChannels
				print(f"showHidden: {showHidden}")
				print(f"cogs: {cogs}")
				# list of commands in each cog

				commands = {}
				for cog in cogs:
					print(f"cog: {cog}")
					# add cog to commands list
					commands[cog] = []
					# get commands in each cog
					_commands = cogs[cog].get_app_commands()
					print(f"app_commands: {_commands}")
					if len(_commands) > 0:
						commands[cog].extend([f"{command.name} - {command.description}" for command in _commands])

					_commands = cogs[cog].get_commands()
					if len(_commands) > 0:
						for command in _commands:
							print(f"command: {command.name} ({command.hidden} + {showHidden})", end=" ")
							if showHidden is False and command.hidden is True:
								print("skipping")
								continue
							print("showing")
							commands[cog].append(f"{ctx.prefix}{command.name} - {command.description}")


				# all commands to embed fields
				for cog in commands:
					if len(commands[cog]) == 0:
						continue
					embed.add_field(
						name = cog,
						value = "\n".join(commands[cog]),
						inline = False,
					)

			embed.set_footer(
				text = f"Powered by {self.bot.__POWERED_BY__}",
			)
			await ctx.send(
				embed = embed
			)



		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild,
			)





async def setup(bot:commands.Bot) -> None:
	try:
		await bot.add_cog(
			Help(
				bot
			)
		)
	except Exception as e:
		raise e

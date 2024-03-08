import discord
from discord import app_commands
from discord.ext import commands
import traceback
import json
import re
import sys
from genericpath import exists


class DriverInformation(discord.ui.Modal):
	# get the driver number and gamertag and rename the user nickname to #number gamertag
	def __init__(self, bot:commands.Bot, interaction:discord.Interaction) -> None:
		super().__init__(title="Driver Information")
		label = bot.get_config(interaction.guild, "label", "driver")
		self.number = discord.ui.TextInput(
			label = label["number"]["name"],
		placeholder = label["number"]["description"],
			style = discord.TextStyle.short,
			required = True,
		)
		self.add_item(self.number)
		self.gamertag = discord.ui.TextInput(
			label = label["gamertag"]["name"],
			placeholder = label["gamertag"]["description"],
			style = discord.TextStyle.short,
			required = True,
		)
		self.bot = bot
		self.add_item(self.gamertag)


	async def on_submit(self, interaction:discord.Interaction) -> None:
		number = self.number.value
		# make sure the number is a number
		if not number.isdigit():
			await interaction.response.send_message(
				"Please enter a valid number",
				ephemeral=True,
			)
			return
		# make sure the number is between 1 and 999
		if int(number) < 1 or int(number) > 999:
			await interaction.response.send_message(
				"Please enter a number between 1 and 999",
				ephemeral=True,
			)
			return
		# convert the number to a int
		number = int(number)
		gamertag = self.gamertag.value
		# make sure the gamertag is not empty
		if len(gamertag) == 0:
			await interaction.response.send_message(
				"Please enter a gamertag",
				ephemeral=True,
			)
			return
		# make sure the gamertag is less than 32 characters
		if len(gamertag) > 32:
			await interaction.response.send_message(
				"Please enter a gamertag less than 32 characters",
				ephemeral=True,
			)
			return
		# make sure the gamertag is alphanumeric or has # or - or space (not tab or newline)
		if not re.match(r"^[a-zA-Z0-9# -]+$", gamertag):
			await interaction.response.send_message(
				"Please enter a gamertag that is alphanumeric or has # or -",
				ephemeral=True,
			)
			return

		jsonFile = f"{sys.path[0]}/guild/{interaction.guild.id}.drivers.json"

		# open the driver json file from the guild folder guild_id.drivers.json, create it if it doesn't exist
		if not exists(jsonFile):
			drivers = {}
			with open(jsonFile, "w") as file:
				json.dump(drivers, file, indent="\t")
		else:
			with open(jsonFile, "r") as file:
				drivers = json.load(file)
		"""
		format:
		{
			"152588151314055168": {
				"number": "21",
				"gamertag": "DxBang"
			}
		}
		"""
		id = str(interaction.user.id)
		# check if the number has already been taken by another user
		for driver, data in drivers.items():
			if data["number"] == number and driver != id:
				await interaction.response.send_message(
					f"The number {data['number']} has already been taken by {data['gamertag']}",
					ephemeral=True,
				)
				return
		# check if the user.id is already in the json file, if it is, update the gamertag, if it isn't, add the user.id and gamertag to the json file
		if id in drivers:
			drivers[id]["number"] = number
			drivers[id]["gamertag"] = gamertag
		else:
			drivers[id] = {
				"number": number,
				"gamertag": gamertag,
			}
		# write the json file
		with open(jsonFile, "w") as file:
			json.dump(drivers, file, indent="\t")
		nick = f"#{number} {gamertag}"
		# check that the bot has the manage nicknames permission
		if not interaction.guild.me.guild_permissions.manage_nicknames:
			await interaction.response.send_message(
				"I don't have permission to manage nicknames",
				ephemeral=True,
			)
			return
		# check that the bot has a higher role than the user
		if interaction.guild.me.top_role.position <= interaction.user.top_role.position:
			await interaction.response.send_message(
				f"I don't have a higher role than you, please set your nickname manually to {nick}",
				ephemeral=True,
			)
			return
		# check if the user has a nickname & if the nickname is the same as the number and gamertag
		if interaction.user.nick == nick:
			await interaction.response.send_message(
				"Your nickname is already set to the number and gamertag, thank you!",
				ephemeral=True,
			)
			return
		# rename the user nickname to #number gamertag
		await interaction.user.edit(
			nick=nick,
		)
		# send a message to the user
		await interaction.response.send_message(
			f"Your number is #{number} and your gamertag is {gamertag}",
			ephemeral=True,
		)
		# send a message to the channel
		await interaction.channel.send(
			f"{interaction.user.mention} has been assigned number #{number} and gamertag {gamertag}",
		)

class Driver(commands.Cog, name="Driver"):
	__slots__ = (
		"bot"
	)
	def __init__(self, bot:commands.Bot) -> None:
		try:
			self.bot = bot
		except Exception as e:
			raise e

	@app_commands.command(
		name = "driver",
		description = "Set the driver number and gamertag and rename the user nickname to #number gamertag.",
	)
	async def driver(self, interaction:discord.Interaction) -> None:
		"""Set the driver number and gamertag and rename the user nickname to #number gamertag."""
		try:
			print(interaction)
			await interaction.response.send_modal(
				DriverInformation(
					bot = self.bot,
					interaction = interaction,
				)
			)
		except Exception as e:
			traceback.print_exc()
			raise e

	@commands.command(
		name = "add_driver",
		description = "Manually add a driver to the list of drivers.",
		usage = "add_driver [@member] [number] [gamertag]",
		hidden = True,
	)
	@commands.has_permissions(manage_nicknames=True)
	async def add_driver(self, ctx:commands.Context, member:discord.Member, number:int, gamertag:str) -> None:
		"""
		Parameters:
		@member: The member to add the driver number and gamertag to.
		number: The driver number.
		gamertag: The driver gamertag.
		e.g.
		{ctx.prefix}add_driver @DxBang 21 DxBang
		"""
		try:
			jsonFile = f"{sys.path[0]}/guild/{ctx.guild.id}.drivers.json"
			# open the driver json file from the guild folder guild_id.drivers.json, create it if it doesn't exist
			if not exists(jsonFile):
				drivers = {}
				with open(jsonFile, "w") as file:
					json.dump(drivers, file, indent="\t")
			else:
				with open(jsonFile, "r") as file:
					drivers = json.load(file)
			"""
			format:
			{
				152588151314055168: {
					"number": "21",
					"gamertag": "DxBang"
				}
			}
			"""
			id = str(member.id)
			# check if the number has already been taken by another user
			for driver, data in drivers.items():
				if data["number"] == number and driver != id:
					await ctx.send(
						f"The number {data['number']} has already been taken by {data['gamertag']}",
					)
					return
			# check if the user.id is already in the json file, if it is, update the gamertag, if it isn't, add the user.id and gamertag to the json file
			if id in drivers:
				drivers[id]["number"] = number
				drivers[id]["gamertag"] = gamertag
			else:
				drivers[id] = {
					"number": number,
					"gamertag": gamertag,
				}
			# write the json file
			with open(jsonFile, "w") as file:
				json.dump(drivers, file, indent="\t")
			nick = f"#{number} {gamertag}"
			# check that the bot has the manage nicknames permission
			if not ctx.guild.me.guild_permissions.manage_nicknames:
				await ctx.send(
					"I don't have permission to manage nicknames",
				)
				return
			# check that the bot has a higher role than the user
			if ctx.guild.me.top_role.position <= member.top_role.position:
				await ctx.send(
					f"I don't have a higher role than {member.mention}, please set your nickname manually to {nick}",
				)
				return
			# check if the user has a nickname & if the nickname is the same as the number and gamertag
			if member.nick == nick:
				await ctx.send(
					f"{member.mention} already has the number and gamertag, thank you!",
				)
				return
			# rename the user nickname to #number gamertag
			await member.edit(
				nick=nick,
			)
			# send a message to the user and the channel
			await ctx.send(
				f"{member.mention} has been assigned number #{number} and gamertag {gamertag}",
			)
		except Exception as e:
			traceback.print_exc()
			raise e



async def setup(bot:commands.Bot) -> None:
	try:
		await bot.add_cog(
			Driver(
				bot
			),
			guilds=bot.guilds,
		)
	except Exception as e:
		raise e

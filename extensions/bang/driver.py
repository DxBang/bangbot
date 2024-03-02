

import discord
from discord import app_commands
from discord.ext import commands


class DriverModal(discord.ui.Modal, title="Driver Information"):

	platform:str = discord.ui.Select(
		placeholder = 'Platform',
		options = [
			discord.SelectOption(label = 'PC', value = 'PC'),
			discord.SelectOption(label = 'Xbox', value = 'Xbox'),
			discord.SelectOption(label = 'Playstation', value = 'Playstation')
		],
	)
	number:int = discord.ui.TextInput(
		label = "Driver Number",
		style = discord.TextStyle.short,
		placeholder = "Number",
		min_length = 1,
		max_length = 3,
		required = True,
	)
	gamerTag:str = discord.ui.TextInput(
		label = "Gamer Tag",
		style = discord.TextStyle.short,
		placeholder = "Gamer Tag",
		min_length = 3,
		max_length = 32,
		required = True,
	)
	async def on_submit(self, interaction: discord.Interaction) -> None:
		return await super().on_submit(interaction)

	def __init__(self):
		super().__init__()

class MyView(discord.ui.View):
    @discord.ui.button(label='Click me!', style=discord.ButtonStyle.primary)
    async def click(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('Button clicked!')

class MyModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="My Modal")

    @discord.ui.button(label='Click me!', style=discord.ButtonStyle.primary)
    async def click(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('Button clicked!')

class Driver(commands.Cog, name="Driver"):
	__slots__ = (
		"bot"
	)
	def __init__(self, bot:commands.Bot) -> None:
		try:
			self.bot = bot
		except Exception as e:
			raise e

	@commands.command(
		hidden = False,
	)
	async def sync(self, ctx:commands.Context) -> None:
		try:
			synced = await self.bot.sync(guild = ctx.guild)
			print(f"Synced {ctx.guild.name} with {len(synced)} command(s)")
			await ctx.send(
				f"Synced {ctx.guild.name} with {len(synced)} command(s)."
			)

		except Exception as e:
			raise e

	@commands.command(
		description = "Register as a driver.",
		hidden = False,
	)
	async def driver(self, interaction:discord.Interaction) -> None:
		# send modal
		await interaction.response.send_modal(
			modal = DriverModal(),
			#epehemeral = True
		)

	@commands.command()
	async def testview(self, ctx):
		view = MyView()
		await ctx.send('Here is a view:', view=view)

	@app_commands.command(
		name = "testmodal",
		description = "Test a modal."
	)
	async def testmodal(self, interaction:discord.Interaction):
		await interaction.response.send_modal(
			modal = MyModal(),
			#epehemeral = True
		)


async def setup(bot:commands.Bot) -> None:
	try:
		await bot.add_cog(
			Driver(
				bot
			)
		)
	except Exception as e:
		raise e

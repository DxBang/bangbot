import bang
import discord
from discord import app_commands
from discord.ext import commands
import traceback

class GamingPlatform(discord.ui.Select):
	def __init__(self):
		options = [
			discord.SelectOption(label='PC', value='pc', emoji='🟥'),
			discord.SelectOption(label='Xbox', value='xbox', emoji='⬛'),
			discord.SelectOption(label='PlayStation', value='playstation', emoji='⬜')
		]
		super().__init__(
			placeholder = 'Choose a platform...',
			options = options
		)
	async def callback(self, interaction: discord.Interaction) -> None:
		self.platform = self.values[0]
		await interaction.response.send_message(
			f"Platform: {self.values[0]}"
		)


class Gaming(commands.Cog, name="Gaming"):
	__slots__ = (
		"bot"
	)
	def __init__(self, bot:bang.Bot) -> None:
		try:
			self.bot = bot
		except Exception as e:
			raise e



async def setup(bot:bang.Bot) -> None:
	try:
		await bot.add_cog(
			Gaming(
				bot
			)
		)
	except Exception as e:
		raise e

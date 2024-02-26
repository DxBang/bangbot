import discord
from discord.ext import commands

class Template(commands.Cog, name="Template"):
	__slots__ = (
		"bot"
	)
	def __init__(self, bot:commands.Bot) -> None:
		try:
			self.bot = bot
		except Exception as e:
			raise e



async def setup(bot:commands.Bot) -> None:
	try:
		await bot.add_cog(
			Template(
				bot
			)
		)
	except Exception as e:
		raise e

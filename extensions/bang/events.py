import discord
from discord.ext import commands

class Events(commands.Cog, name="Events"):
	def __init__(self, config):
		self.config = config

	# @commands.hybrid_command()
	@commands.command(
		description="Create an event for people to sign up for with reactions for going, maybe, and not going.",
		hidden=False,
	)
	@commands.guild_only()
	async def event(self, )


async def setup(bot:commands.Bot) -> None:
	try:
		await bot.add_cog(
			Events(
				bot
			)
		)
	except Exception as e:
		raise e

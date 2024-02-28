import discord
from discord.ext import commands

class Event(commands.Cog, name="Event Management"):
	__slots__ = (
		"bot",
	)
	def __init__(self, bot:commands.Bot) -> None:
		try:
			self.bot = bot
		except Exception as e:
			raise e

	# @commands.hybrid_command()
	@commands.command(
		description = "Create an event for people to sign up for with reactions for going, maybe, and not going.",
		hidden = False,
	)
	@commands.guild_only()
	async def event(self, ctx:commands.Context) -> None:
		"""Create an event for people to sign up for with reactions for going, maybe, and not going."""
		try:
			title = ctx.message.content.split("\n", 1)[0].split(" ", 1)[1].strip()
			description = ctx.message.content.split("\n", 1)[1].strip()
			embed = self.bot.embed(
				ctx = ctx,
				title = title,
				description = description,
				bot = True,
			)
			embed.set_footer(
				text = f"Powered by {self.bot.__POWERED_BY__}",
			)
			embed.set_author(
				name = ctx.guild.name,
				icon_url = ctx.guild.icon,
			)
			event_reaction = self.bot.get_config(ctx.guild, "event")
			for reaction in ctx.message.reactions:
				users = await reaction.users().flatten()
				if reaction.emoji == event_reaction["accept"]["emoji"]:
					going = users
				elif reaction.emoji == event_reaction["maybe"]["emoji"]:
					maybe = users
				elif reaction.emoji == event_reaction["decline"]["emoji"]:
					decline = users
			embed.add_field(
				name = event_reaction["accept"]["name"],
				value = "\n",
				inline = True,
			)
			embed.add_field(
				name = event_reaction["maybe"]["name"],
				value = "\n",
				inline = True,
			)
			embed.add_field(
				name = event_reaction["decline"]["name"],
				value = "\n",
				inline = True,
			)
			await ctx.message.delete()
			message = await ctx.send(
				embed = embed,
			)
			await message.add_reaction(event_reaction["accept"]["emoji"])
			await message.add_reaction(event_reaction["maybe"]["emoji"])
			await message.add_reaction(event_reaction["decline"]["emoji"])
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild
			)

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload:discord.RawReactionActionEvent) -> None:
		"""Add a user to the list of people going to an event."""
		try:
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
			user = self.bot.get_user(payload.user_id)
			if user.id == self.bot.user.id:
				return
			if len(message.embeds) == 0:
				return
			event_reaction = self.bot.get_config(message.guild, "event")
			embed = message.embeds[0]
			if len(embed.fields) != 3:
				return
			fields = embed.fields
			if fields[0].name != event_reaction["accept"]["name"] and\
				fields[1].name != event_reaction["maybe"]["name"] and\
				fields[2].name != event_reaction["decline"]["name"]:
				print("not an event message")
				return
			valid_reaction = []
			for er in event_reaction:
				valid_reaction.append(event_reaction[er]["emoji"])
			if payload.emoji.name not in valid_reaction:
				return await message.remove_reaction(payload.emoji, user)
			goings = fields[0].value.split("\n")
			maybes = fields[1].value.split("\n")
			declines = fields[2].value.split("\n")
			#if message.author.id != self.bot.user.id:
			#	return
			emoji = str(payload.emoji)
			print(f"emoji: {emoji}")
			# remove the user from the list
			if user.mention in goings:
				goings.remove(user.mention)
			elif user.mention in maybes:
				maybes.remove(user.mention)
			elif user.mention in declines:
				declines.remove(user.mention)
			# add the user to the list
			if emoji == event_reaction["accept"]["emoji"]:
				goings.append(user.mention)
			elif emoji == event_reaction["maybe"]["emoji"]:
				maybes.append(user.mention)
			elif emoji == event_reaction["decline"]["emoji"]:
				declines.append(user.mention)
			# update the embed
			embed.set_field_at(
				0,
				name = event_reaction["accept"]["name"],
				value = "\n".join(goings),
				inline = True,
			)
			embed.set_field_at(
				1,
				name = event_reaction["maybe"]["name"],
				value = "\n".join(maybes),
				inline = True,
			)
			embed.set_field_at(
				2,
				name = event_reaction["decline"]["name"],
				value = "\n".join(declines),
				inline = True,
			)
			await message.edit(
				embed = embed,
			)
			for reaction in message.reactions:
				if reaction.emoji == emoji:
					continue
				users = [user async for user in reaction.users()]
				if user in users:
					await message.remove_reaction(reaction.emoji, user)
		except Exception as e:
			print(f"error: {e}")
			raise e

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload:discord.RawReactionActionEvent) -> None:
		"""Remove a user from the list of people going to an event."""
		try:
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
			user = self.bot.get_user(payload.user_id)
			if user.id == self.bot.user.id:
				return
			if len(message.embeds) == 0:
				return
			event_reaction = self.bot.get_config(message.guild, "event")
			if payload.emoji.name not in event_reaction.values():
				print("not an event reaction")
				return
			embed = message.embeds[0]
			if len(embed.fields) != 3:
				return
			fields = embed.fields
			goings = fields[0].value.split("\n")
			maybes = fields[1].value.split("\n")
			declines = fields[2].value.split("\n")
			if message.author.id != self.bot.user.id:
				print("not a bot message")
				return
			if len(message.embeds) == 0:
				print("no embed")
				return
			emoji = str(payload.emoji)
			if emoji == event_reaction["accept"]["emoji"] and user.mention in goings:
				goings.remove(user.mention)
			elif emoji == event_reaction["maybe"]["emoji"] and user.mention in maybes:
				maybes.remove(user.mention)
			elif emoji == event_reaction["decline"]["emoji"] and user.mention in declines:
				declines.remove(user.mention)
			embed.set_field_at(
				0,
				name = event_reaction["accept"]["name"],
				value = "\n".join(goings),
				inline = True,
			)
			embed.set_field_at(
				1,
				name = event_reaction["maybe"]["name"],
				value = "\n".join(maybes),
				inline = True,
			)
			embed.set_field_at(
				2,
				name = event_reaction["decline"]["name"],
				value = "\n".join(declines),
				inline = True,
			)
			await message.edit(
				embed = embed,
			)
		except Exception as e:
			print(f"error: {e}")
			raise e



async def setup(bot:commands.Bot) -> None:
	try:
		await bot.add_cog(
			Event(
				bot
			)
		)
	except Exception as e:
		raise e

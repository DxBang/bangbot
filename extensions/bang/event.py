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
	@commands.has_permissions(moderate_members=True)
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
			label = self.bot.get_config(ctx.guild, "label", "event")
			config = self.bot.get_config(ctx.guild, "event")
			embed.add_field(
				name = label["accept"]["name"],
				value = "\n",
				inline = True,
			)
			embed.add_field(
				name = label["maybe"]["name"],
				value = "\n",
				inline = True,
			)
			embed.add_field(
				name = label["decline"]["name"],
				value = "\n",
				inline = True,
			)
			files = None
			if len(ctx.message.attachments) > 0:
				if config["attachment"]["thumbnail"]:
					embed.set_thumbnail(
						url = ctx.message.attachments[0].url
					)
				if config["attachment"]["download"] and config["attachment"]["image"]:
					file = await self.bot.download_attachment(ctx.message.attachments[0])
					files = [file]
					embed.set_image(
						url = "attachment://" + file.filename
					)
				elif config["attachment"]["image"]:
					embed.set_image(
						url = ctx.message.attachments[0].url
					)
			await ctx.message.delete()
			message = await ctx.send(
				embed = embed,
				files = files,
			)
			await message.add_reaction(label["accept"]["emoji"])
			await message.add_reaction(label["maybe"]["emoji"])
			await message.add_reaction(label["decline"]["emoji"])
		except Exception as e:
			await self.bot.error(
				e,
				guild = ctx.guild
			)

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload:discord.RawReactionActionEvent) -> None:
		"""Add a user to the list of people going/maybe/not going to an event."""
		try:
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
			user = self.bot.get_user(payload.user_id)
			if user.id == self.bot.user.id:
				return
			if len(message.embeds) == 0:
				return
			label = self.bot.get_config(message.guild, "label", "event")
			embed = message.embeds[0]
			if len(embed.fields) != 3:
				return
			fields = embed.fields
			if fields[0].name != label["accept"]["name"] and\
				fields[1].name != label["maybe"]["name"] and\
				fields[2].name != label["decline"]["name"]:
				print("not an event message")
				return
			valid_reaction = []
			for er in label:
				valid_reaction.append(label[er]["emoji"])
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
			if emoji == label["accept"]["emoji"]:
				goings.append(user.mention)
			elif emoji == label["maybe"]["emoji"]:
				maybes.append(user.mention)
			elif emoji == label["decline"]["emoji"]:
				declines.append(user.mention)
			# update the embed
			embed.set_field_at(
				0,
				name = label["accept"]["name"],
				value = "\n".join(goings),
				inline = True,
			)
			embed.set_field_at(
				1,
				name = label["maybe"]["name"],
				value = "\n".join(maybes),
				inline = True,
			)
			embed.set_field_at(
				2,
				name = label["decline"]["name"],
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
			label = self.bot.get_config(message.guild, "event")
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
			if emoji == label["accept"]["emoji"] and user.mention in goings:
				goings.remove(user.mention)
			elif emoji == label["maybe"]["emoji"] and user.mention in maybes:
				maybes.remove(user.mention)
			elif emoji == label["decline"]["emoji"] and user.mention in declines:
				declines.remove(user.mention)
			embed.set_field_at(
				0,
				name = label["accept"]["name"],
				value = "\n".join(goings),
				inline = True,
			)
			embed.set_field_at(
				1,
				name = label["maybe"]["name"],
				value = "\n".join(maybes),
				inline = True,
			)
			embed.set_field_at(
				2,
				name = label["decline"]["name"],
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

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
		hidden = True,
		usage = "event <title>\n<description>",
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def event(self, ctx:commands.Context) -> None:
		"""
		Use the following format to create an event:
		```
		{ctx.prefix}event The next race at Silverstone

		We will be racing at Silverstone next week. Please react to the message to let us know if you are going, maybe, or not going.
		So sign up @drivers and let us know if you are going to be there.
		```
		Depending on the configuration, you can mention roles to lock the reactions to that role or have it completely locked to specific role(s).
		A single image can be attached to the event message, and it can be set to be a thumbnail or the main image in the configuration.
		"""
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
			mention = None
			mentions = []
			roles = self.bot.get_config(ctx.guild, "event", "roles")
			if isinstance(roles, list) and len(roles) > 0:
				mentions.extend([role.mention for role in ctx.guild.roles if role.id in roles])
			label = self.bot.get_config(ctx.guild, "label", "event")
			config = self.bot.get_config(ctx.guild, "event")
			embed.add_field(
				name = f"{label['accept']['emoji']} {label['accept']['name']}",
				value = "\n",
				inline = True,
			)
			embed.add_field(
				name = f"{label['maybe']['emoji']} {label['maybe']['name']}",
				value = "\n",
				inline = True,
			)
			embed.add_field(
				name = f"{label['decline']['emoji']} {label['decline']['name']}",
				value = "\n",
				inline = True,
			)
			if len(ctx.message.role_mentions) > 0:
				mentions.extend([role.mention for role in ctx.message.role_mentions])
			mention = " ".join(mentions)
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
				content = mention,
				embed = embed,
				files = files,
			)
			await message.add_reaction(label['accept']['emoji'])
			await message.add_reaction(label['maybe']['emoji'])
			await message.add_reaction(label['decline']['emoji'])
		except Exception as e:
			await self.bot.error(
				e,
				ctx = ctx,
			)

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload:discord.RawReactionActionEvent) -> None:
		"""Add a user to the list of people going/maybe/not going to an event."""
		try:
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
			#author = message.author
			guild = self.bot.get_guild(payload.guild_id)
			member = guild.get_member(payload.user_id)
			if member.id == self.bot.user.id:
				# bot predefined reaction
				return
			if len(message.embeds) == 0:
				return
			roles = self.bot.get_config(message.guild, "event", "roles")
			# roles format: [729023577977782322, 729023577977782324] or boolean True|False
			if isinstance(roles, list) and len(roles) > 0:
				found = False
				for role in roles:
					if role in [role.id for role in member.roles]:
						found = True
						break
				if not found:
					return await message.remove_reaction(payload.emoji, member)
			elif isinstance(roles, bool) and roles == True:
				roles = [role.id for role in message.role_mentions]
				if len(roles) > 0:
					found = False
					if len(roles) > 0:
						for role in roles:
							if role in [role.id for role in member.roles]:
								found = True
								break
					if not found:
						return await message.remove_reaction(payload.emoji, member)
			label = self.bot.get_config(message.guild, "label", "event")
			embed = message.embeds[0]
			if len(embed.fields) != 3:
				return
			fields = embed.fields
			if label['accept']['emoji'] not in fields[0].name and label['accept']['name'] not in fields[0].name:
				return
			if label['maybe']['emoji'] not in fields[1].name and label['maybe']['name'] not in fields[1].name:
				return
			if label['decline']['emoji'] not in fields[2].name and label['decline']['name'] not in fields[2].name:
				return
			valid_reaction = []
			for er in label:
				valid_reaction.append(label[er]["emoji"])
			if payload.emoji.name not in valid_reaction:
				return await message.remove_reaction(payload.emoji, member)
			goings = fields[0].value.split("\n")
			maybes = fields[1].value.split("\n")
			declines = fields[2].value.split("\n")
			emoji = str(payload.emoji)
			# remove the user from the list
			if member.mention in goings:
				goings.remove(member.mention)
			elif member.mention in maybes:
				maybes.remove(member.mention)
			elif member.mention in declines:
				declines.remove(member.mention)
			# add the user to the list
			if emoji == label['accept']['emoji']:
				goings.append(member.mention)
			elif emoji == label['maybe']['emoji']:
				maybes.append(member.mention)
			elif emoji == label['decline']['emoji']:
				declines.append(member.mention)
			# update the embed
			embed.set_field_at(
				0,
				name = f"{label['accept']['emoji']} {label['accept']['name']}",
				value = "\n".join(goings),
				inline = True,
			)
			embed.set_field_at(
				1,
				name = f"{label['maybe']['emoji']} {label['maybe']['name']}",
				value = "\n".join(maybes),
				inline = True,
			)
			embed.set_field_at(
				2,
				name = f"{label['decline']['emoji']} {label['decline']['name']}",
				value = "\n".join(declines),
				inline = True,
			)
			await message.edit(
				embed = embed,
			)
			for reaction in message.reactions:
				if reaction.emoji == emoji:
					continue
				members = [user async for user in reaction.users()]
				if member in members:
					await message.remove_reaction(reaction.emoji, member)
		except Exception as e:
			print(f"error: {e}")
			raise e

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload:discord.RawReactionActionEvent) -> None:
		"""Remove a user from the list of people going to an event."""
		try:
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
			guild = self.bot.get_guild(payload.guild_id)
			member = guild.get_member(payload.user_id)
			#user = self.bot.get_user(payload.user_id)
			if member.id == self.bot.user.id:
				return
			if len(message.embeds) == 0:
				return
			label = self.bot.get_config(message.guild, "label", "event")
			embed = message.embeds[0]
			if len(embed.fields) != 3:
				return
			fields = embed.fields
			if label['accept']['emoji'] not in fields[0].name and label['accept']['name'] not in fields[0].name:
				return
			if label['maybe']['emoji'] not in fields[1].name and label['maybe']['name'] not in fields[1].name:
				return
			if label['decline']['emoji'] not in fields[2].name and label['decline']['name'] not in fields[2].name:
				return
			goings = fields[0].value.split("\n")
			maybes = fields[1].value.split("\n")
			declines = fields[2].value.split("\n")
			if len(message.embeds) == 0:
				return
			emoji = str(payload.emoji)
			update = False
			if emoji == label['accept']['emoji'] and member.mention in goings:
				goings.remove(member.mention)
				update = True
			elif emoji == label['maybe']['emoji'] and member.mention in maybes:
				maybes.remove(member.mention)
				update = True
			elif emoji == label['decline']['emoji'] and member.mention in declines:
				declines.remove(member.mention)
				update = True
			if update:
				embed.set_field_at(
					0,
					name = f"{label['accept']['emoji']} {label['accept']['name']}",
					value = "\n".join(goings),
					inline = True,
				)
				embed.set_field_at(
					1,
					name = f"{label['maybe']['emoji']} {label['maybe']['name']}",
					value = "\n".join(maybes),
					inline = True,
				)
				embed.set_field_at(
					2,
					name = f"{label['decline']['emoji']} {label['decline']['name']}",
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

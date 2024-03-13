import discord
from discord.ext import commands
import traceback

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
				content = f"📅 {mention}",
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

	def build_embed_fields(self, embed:discord.Embed, member:discord.Member, action:str, emoji:discord.Emoji) -> tuple[discord.Embed, str]:
		"""Build a list of embed fields from an event sign up."""
		try:
			print(f"build_embed_fields: {embed}, {member}, {action}, {emoji}")
			label = self.bot.get_config(member.guild, "label", "event")
			if label['accept']['emoji'] not in embed.fields[0].name and label['accept']['name'] not in embed.fields[0].name:
				return embed, "ignore"
			if label['maybe']['emoji'] not in embed.fields[1].name and label['maybe']['name'] not in embed.fields[1].name:
				return embed, "ignore"
			if label['decline']['emoji'] not in embed.fields[2].name and label['decline']['name'] not in embed.fields[2].name:
				return embed, "ignore"
			items_limit = 20
			column = {
				"accept": 0,
				"maybe": 1,
				"decline": 2,
			}
			row = 0
			accepts = []
			maybes = []
			declines = []
			field_multiplier = 3
			for idx, field in enumerate(embed.fields):
				if idx % field_multiplier == column['accept']: # 0
					if len(field.value.strip()) > 0:
						accepts.extend(field.value.strip().split("\n"))
				elif idx % field_multiplier == column['maybe']: # 1
					if len(field.value.strip()) > 0:
						maybes.extend(field.value.strip().split("\n"))
				elif idx % field_multiplier == column['decline']: # 2
					if len(field.value.strip()) > 0:
						declines.extend(field.value.strip().split("\n"))
				else:
					print("error")
			# make sure the list is unique
			accepts = list(set(accepts))
			maybes = list(set(maybes))
			declines = list(set(declines))
			if action == "add":
				valid_reaction = []
				for er in label:
					valid_reaction.append(label[er]["emoji"])
				if emoji.name not in valid_reaction:
					return embed, "remove"
				if emoji.name == label['accept']['emoji']:
					action = "update"
					accepts.append(member.mention)
					# remove from maybes and declines
					if member.mention in maybes:
						maybes.remove(member.mention)
					if member.mention in declines:
						declines.remove(member.mention)
				elif emoji.name == label['maybe']['emoji']:
					action = "update"
					maybes.append(member.mention)
					# remove from accepts and declines
					if member.mention in accepts:
						accepts.remove(member.mention)
					if member.mention in declines:
						declines.remove(member.mention)
				elif emoji.name == label['decline']['emoji']:
					action = "update"
					declines.append(member.mention)
					# remove from accepts and maybes
					if member.mention in accepts:
						accepts.remove(member.mention)
					if member.mention in maybes:
						maybes.remove(member.mention)
				else:
					return embed, "ignore"
			elif action == "remove":
				if emoji.name == label['accept']['emoji'] and member.mention in accepts:
					action = "update"
					accepts.remove(member.mention)
				elif emoji.name == label['maybe']['emoji'] and member.mention in maybes:
					action = "update"
					maybes.remove(member.mention)
				elif emoji.name == label['decline']['emoji'] and member.mention in declines:
					action = "update"
					declines.remove(member.mention)
				else:
					return embed, "ignore"
			else:
				return embed, "ignore"
			# split the list into multiple lists if the list has more than items_limit members
			accepts = [accepts[i:i + items_limit] for i in range(0, len(accepts), items_limit)]
			maybes = [maybes[i:i + items_limit] for i in range(0, len(maybes), items_limit)]
			declines = [declines[i:i + items_limit] for i in range(0, len(declines), items_limit)]
			largest = max(len(accepts), len(maybes), len(declines))
			# create the fields
			embed.clear_fields()
			for row in range(largest):
				accept = accepts[row] if row < len(accepts) else []
				maybe = maybes[row] if row < len(maybes) else []
				decline = declines[row] if row < len(declines) else []
				for col, members in enumerate([accept, maybe, decline]):
					if col == column['accept']:
						name = f"{label['accept']['emoji']} {label['accept']['name']}"
					elif col == column['maybe']:
						name = f"{label['maybe']['emoji']} {label['maybe']['name']}"
					elif col == column['decline']:
						name = f"{label['decline']['emoji']} {label['decline']['name']}"
					embed.add_field(
						name = name,
						value = "\n".join(members),
						inline = True,
					)
			return embed, action
		except Exception as e:
			raise e

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload:discord.RawReactionActionEvent) -> None:
		"""Add a user to the list of people going/maybe/not going to an event."""
		try:
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
			guild = self.bot.get_guild(payload.guild_id)
			member = guild.get_member(payload.user_id)
			if member.id == self.bot.user.id:
				# bot predefined reaction
				return
			if len(message.embeds) == 0:
				return
			if len(message.embeds[0].fields) < 3:
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
			embed, action = self.build_embed_fields(message.embeds[0], member, "add", payload.emoji)
			print(f"add action: {action}")
			if action == "remove":
				return await message.remove_reaction(payload.emoji, member)
			if action == "update":
				await message.edit(
					embed = embed,
				)
			for reaction in message.reactions:
				if reaction.emoji == payload.emoji.name:
					continue
				members = [user async for user in reaction.users()]
				if member in members:
					await message.remove_reaction(reaction.emoji, member)
		except discord.HTTPException as e:
			ctx = await self.bot.get_context(message)
			if ctx:
				await ctx.send(
					"HTTPException: {e}",
					delete_after = 60,
					ephemeral = True,
					reference = message,
				)
		except discord.RateLimited as e:
			ctx = await self.bot.get_context(message)
			if ctx: # can we even report this to the user?
				await ctx.send(
					"RateLimited: {e}",
					delete_after = 60,
					ephemeral = True,
					reference = message,
				)
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
			if len(message.embeds[0].fields) < 3:
				return
			embed, action = self.build_embed_fields(message.embeds[0], member, "remove", payload.emoji)
			print(f"remove action: {action}")
			if action == "update":
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

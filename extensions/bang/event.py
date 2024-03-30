import bang
import discord
from discord.ext import commands
import traceback
from bang.acc import ACC
from bang.human import Human
from bang.dest import Dest
import asyncio

class Event(commands.Cog, name="Event Management"):
	__slots__ = (
		"bot",
	)
	def __init__(self, bot:bang.Bot) -> None:
		try:
			self.bot = bot
		except Exception as e:
			raise e

	async def convertEmoji(self, ctx:commands.Context, emoji:discord.Emoji|discord.PartialEmoji|str) -> discord.Emoji:
		try:
			if isinstance(emoji, discord.Emoji):
				return emoji
			if isinstance(emoji, discord.PartialEmoji):
				return emoji
			# check if the emoji is a custom emoji
			if emoji.startswith(":") and emoji.endswith(":"):
				return discord.utils.get(
					ctx.guild.emojis,
					name=emoji.strip(":")
				)
			# check if the emoji is a custom emoji with an ID
			if emoji.startswith("<") and emoji.endswith(">"):
				return discord.utils.get(
					ctx.guild.emojis,
					id=int(emoji.strip("<").strip(">").split(":")[-1])
				)
			# return the default emoji
			return discord.PartialEmoji(
				name = emoji,
			)
		except commands.BadArgument:
			raise commands.BadArgument(f"Invalid emoji: {emoji}")

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

		We will be racing at Silverstone next week....
		```
		If you want to use the date and time fields, you can use the following format:
		```
		{ctx.prefix}event The next event at Silverstone
		date: 2024-12-31
		time: 20:00
		We will be racing at Silverstone next week....
		```
		Note:
		That when using the date and time fields, it will be removed from the description.
		If you want to display the date and time in the event message, write them twice.
		---
		Depending on the configuration, you can mention roles to lock the reactions to that role or have it completely locked to specific role(s).
		A single image can be attached to the event message, and it can be set to be a thumbnail or the main image in the configuration.
		"""
		try:
			title = ctx.message.content.split("\n", 1)[0].split(" ", 1)[1].strip()
			description = ctx.message.content.split("\n", 1)[1].strip().split("\n")
			# find the first line in description which starts with "date:" and "time:" and parse the date and time to epoch, then remove the line from the description
			date = None
			time = None
			epoch = None
			delete = []
			for idx, line in enumerate(description):
				if date is None:
					if line.lower().startswith("date:"):
						date = line.split(" ", 1)[1].strip()
						# remove the line from the description
						delete.append(idx)
				if time is None:
					if line.lower().startswith("time:"):
						time = line.split(" ", 1)[1].strip()
						# remove the line from the description
						delete.append(idx)
			delete = delete[::-1]
			for idx in delete:
				del description[idx]
			description = "\n".join(description).strip()
			embed = self.bot.embed(
				ctx = ctx,
				title = title,
				description = description,
				bot = True,
			)
			embed.set_footer(
				text = self.bot.__POWERED_BY__,
			)
			embed.set_author(
				name = ctx.guild.name,
				icon_url = ctx.guild.icon,
			)
			mention = None
			mentions = []
			roles = self.bot.getConfig(ctx.guild, "event", "roles")
			if isinstance(roles, list) and len(roles) > 0:
				mentions.extend([role.mention for role in ctx.guild.roles if role.id in roles])
			label = self.bot.getConfig(ctx.guild, "label", "event")
			# fix emojis
			for l in label:
				if isinstance(label[l], dict):
					label[l]["emoji"] = await self.convertEmoji(ctx, label[l]["emoji"])
			config = self.bot.getConfig(ctx.guild, "event")
			if date is not None:
				epoch = ACC.dateToEpoch(
					date,
					time,
					self.bot.getConfig(ctx.guild, "timezone")
				)
			if epoch is not None:
				embed.add_field(
					name = f"{label['date']['emoji']} {label['date']['name']}",
					value = f"<t:{epoch}:D>",
					inline = True,
				)
				embed.add_field(
					name = f"{label['time']['emoji']} {label['time']['name']}",
					value = f"<t:{epoch}:t>",
					inline = True,
				)
				embed.add_field(
					name = f"{label['countdown']['emoji']} {label['countdown']['name']}",
					value = f"<t:{epoch}:R>",
					inline = True,
				)
				if config['use_separator']:
					embed.add_field(
						name = "\u200b",
						value = "\n",
						inline = False,
					)
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
				file = await self.bot.downloadAttachment(ctx.message.attachments[0])
				files = [file]
				if config["attachment"]["thumbnail"]:
					embed.set_thumbnail(
						url = f"attachment://{file.filename}"
					)
				if config["attachment"]["image"]:
					embed.set_image(
						url = f"attachment://{file.filename}"
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
			file = Dest.join(
				self.bot.getTemp("events"),
				f"{message.id}.json",
			)
			Dest.json.save(
				file,
				{
					"channel": message.channel.id,
					"title": title,
					"description": description,
					"epoch": epoch,
					"accept": [],
					"maybe": [],
					"decline": [],
				}
			)
		except Exception as e:
			await self.bot.error(
				e,
				ctx = ctx,
			)

	async def handleReaction(self, ctx:commands.Context, member:discord.Member, action:str, emoji:discord.Emoji|discord.PartialEmoji|str) -> tuple[discord.Embed, str]:
		"""Build a list of embed fields from an event sign up."""
		try:
			embed = ctx.message.embeds[0]
			print(f"handleReaction: {embed}, {member}, {action}, {type(emoji)} {emoji}")
			file = Dest.join(
				self.bot.getTemp("events"),
				f"{ctx.message.id}.json",
			)
			if Dest.exists(file) is False:
				return embed, "ignore"
			data = Dest.json.load(file)
			if data is None:
				return embed, "ignore"
			label = self.bot.getConfig(member.guild, "label", "event")
			emoji = str(await self.convertEmoji(ctx, emoji))
			for l in label:
				if isinstance(label[l], dict):
					label[l]["emoji"] = str(await self.convertEmoji(ctx, label[l]["emoji"]))
			first = 0
			# check if the embed has date, time, and countdown fields
			if label['date']['emoji'] in embed.fields[0].name and\
				label['time']['emoji'] in embed.fields[1].name and\
				label['countdown']['emoji'] in embed.fields[2].name:
				first = 3
				print("has date, time, and countdown fields")
				if embed.fields[3].name == "\u200b":
					print("has separator")
					first = 4
			if label['accept']['emoji'] not in embed.fields[0 + first].name:
				print(f"failed accept: {label['accept']['emoji']}")
				return embed, "ignore"
			if label['maybe']['emoji'] not in embed.fields[1 + first].name:
				print(f"failed maybe: {label['maybe']['emoji']}")
				return embed, "ignore"
			if label['decline']['emoji'] not in embed.fields[2 + first].name:
				print(f"failed decline: {label['decline']['emoji']}")
				return embed, "ignore"
			items_limit = 20
			column = {
				"accept": 0,
				"maybe": 1,
				"decline": 2,
			}
			accepts = []
			maybes = []
			declines = []
			if "accept" in data:
				accepts = data["accept"]
			if "maybe" in data:
				maybes = data["maybe"]
			if "decline" in data:
				declines = data["decline"]
			if action == "add":
				print(f"add: {emoji}")
				valid_reaction = []
				for k in ["accept", "maybe", "decline"]:
					if isinstance(label[k], dict):
						valid_reaction.append(label[k]["emoji"])
				if emoji not in valid_reaction:
					return embed, "remove"
				# check if the member.id is already in the list of accepts, maybes, or declines
				action = "update"
				if emoji == label['accept']['emoji'] and member.id not in [m['id'] for m in accepts]:
					print(f"add accept: {member.display_name}")
					accepts.append(
						{
							"id": member.id,
							"name": member.display_name,
						}
					)
					# remove the member from the maybes and declines list
					if member.id in [m['id'] for m in maybes]:
						maybes = [m for m in maybes if m['id'] != member.id]
					if member.id in [m['id'] for m in declines]:
						declines = [m for m in declines if m['id'] != member.id]
				elif emoji == label['maybe']['emoji'] and member.id not in [m['id'] for m in maybes]:
					print(f"add maybe: {member.display_name}")
					maybes.append(
						{
							"id": member.id,
							"name": member.display_name,
						}
					)
					# remove the member from the accepts and declines list
					if member.id in [m['id'] for m in accepts]:
						accepts = [m for m in accepts if m['id'] != member.id]
					if member.id in [m['id'] for m in declines]:
						declines = [m for m in declines if m['id'] != member.id]
				elif emoji == label['decline']['emoji'] and member.id not in [m['id'] for m in declines]:
					print(f"add decline: {member.display_name}")
					declines.append(
						{
							"id": member.id,
							"name": member.display_name,
						}
					)
					# remove the member from the accepts and maybes list
					if member.id in [m['id'] for m in accepts]:
						accepts = [m for m in accepts if m['id'] != member.id]
					if member.id in [m['id'] for m in maybes]:
						maybes = [m for m in maybes if m['id'] != member.id]
				else:
					return embed, "ignore"
			elif action == "remove":
				print(f"remove: {emoji}")
				action = "update"
				if emoji == label['accept']['emoji'] and member.id in [m['id'] for m in accepts]:
					accepts = [m for m in accepts if m['id'] != member.id]
				elif emoji == label['maybe']['emoji'] and member.id in [m['id'] for m in maybes]:
					maybes = [m for m in maybes if m['id'] != member.id]
				elif emoji == label['decline']['emoji'] and member.id in [m['id'] for m in declines]:
					declines = [m for m in declines if m['id'] != member.id]
				else:
					print(f"not found")
					return embed, "ignore"
			else:
				return embed, "ignore"
			# make unique
			#accepts = list(set(accepts))
			#maybes = list(set(maybes))
			#declines = list(set(declines))
			# split the list into multiple lists if the list has more than items_limit members
			_accepts = [accepts[i:i + items_limit] for i in range(0, len(accepts), items_limit)]
			_maybes = [maybes[i:i + items_limit] for i in range(0, len(maybes), items_limit)]
			_declines = [declines[i:i + items_limit] for i in range(0, len(declines), items_limit)]
			largest = max(len(_accepts), len(_maybes), len(_declines), 1)
			# remove old fields
			for r in range(len(embed.fields)-1, first-1, -1):
				print(f"remove: {r}, {embed.fields[r].name}")
				embed.remove_field(r)
			# recreate the fields
			for r in range(largest):
				accept = _accepts[r] if r < len(_accepts) else []
				maybe = _maybes[r] if r < len(_maybes) else []
				decline = _declines[r] if r < len(_declines) else []
				for col, members in enumerate([accept, maybe, decline]):
					if col == column['accept']:
						name = f"{label['accept']['emoji']} {label['accept']['name']}"
					elif col == column['maybe']:
						name = f"{label['maybe']['emoji']} {label['maybe']['name']}"
					elif col == column['decline']:
						name = f"{label['decline']['emoji']} {label['decline']['name']}"
					embed.add_field(
						name = name,
						value = "\n".join([f"{member['name']}" for member in members]) if len(members) > 0 else "\u200b",
						inline = True,
					)
			# save the data
			data["accept"] = accepts
			data["maybe"] = maybes
			data["decline"] = declines
			Dest.json.save(
				file,
				data
			)
			return embed, action
		except Exception as e:
			raise e

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload:discord.RawReactionActionEvent) -> None:
		"""Add a user to the list of people going/maybe/not going to an event."""
		try:
			print(f"on_raw_reaction_add: {type(payload.emoji)} {payload.emoji}")
			message = await self.bot.get_channel(
				payload.channel_id
			).fetch_message(
				payload.message_id
			)
			member = message.guild.get_member(payload.user_id)
			ctx = await self.bot.get_context(message)
			if member.id == self.bot.user.id:
				# bot predefined reaction
				return
			if len(message.embeds) == 0:
				return
			if len(message.embeds[0].fields) < 3:
				return
			roles = self.bot.getConfig(message.guild, "event", "roles")
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
			embed, action = await self.handleReaction(
				ctx,
				member,
				"add",
				payload.emoji,
			)
			print(f"add action: {action}")
			if action == "remove":
				return await message.remove_reaction(payload.emoji, member)
			if action == "update":
				await message.edit(
					embed = embed,
					attachments = message.attachments,
				)
			for reaction in message.reactions:
				if str(reaction.emoji) == str(payload.emoji):
					continue
				members = [user async for user in reaction.users()]
				if member in members:
					await message.remove_reaction(reaction.emoji, member)
		except discord.HTTPException as e:
			if ctx:
				await ctx.send(
					"HTTPException: {e}",
					delete_after = 60,
					ephemeral = True,
					reference = message,
				)
		except discord.RateLimited as e:
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
			message = await self.bot.get_channel(
				payload.channel_id
			).fetch_message(
				payload.message_id
			)
			member = message.guild.get_member(payload.user_id)
			ctx = await self.bot.get_context(message)
			#user = self.bot.get_user(payload.user_id)
			if member.id == self.bot.user.id:
				return
			if len(message.embeds) == 0:
				return
			if len(message.embeds[0].fields) < 3:
				return
			embed, action = await self.handleReaction(
				ctx,
				member,
				"remove",
				payload.emoji,
			)
			print(f"remove action: {action}")
			if action == "update":
				await message.edit(
					embed = embed,
					attachments = message.attachments,
				)
		except Exception as e:
			print(f"error: {e}")
			raise e


	@commands.command()
	async def test(self, ctx:commands.Context) -> None:
		try:
			file = discord.File('image/dems2024-logo-wht.png', filename='new_image.png')
			embed = discord.Embed(
				title="Image Test",
				description="Is this a bug?",
			)
			embed.set_image(url="attachment://new_image.png")
			embed.add_field(
				name="Status",
				value="New",
			)
			message = await ctx.send(
				file=file,
				embed=embed,
			)
			async with ctx.typing():
				await asyncio.sleep(5)
				embed = message.embeds[0]
				embed.set_field_at(
					0,
					name="Status",
					value="Edited...",
				)
				#embed.set_image(
				#	url=message.embeds[0].image.url,
				#)
				await message.edit(
					embed=embed,
					attachments=message.attachments,
				)
				return
		except Exception as e:
			print(f"error: {e}")
			raise e

async def setup(bot:bang.Bot) -> None:
	try:
		await bot.add_cog(
			Event(
				bot
			)
		)
	except Exception as e:
		raise e

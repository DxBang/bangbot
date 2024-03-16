"""
Login to ACC Dedicated Server via FTP and get the race results.
"""
import ftplib
from datetime import datetime
import re
#from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands
#from discord import app_commands
from bang.dest import Dest
from bang.acc import ACC
import traceback

class ACCRace(commands.Cog, name="Race Results"):
	__slots__ = (
		"bot",
		"ftp",
	)
	def __init__(self, bot:commands.Bot) -> None:
		try:
			self.bot = bot
			self.ftp = ftplib.FTP()
		except Exception as e:
			raise e

	def get_results(self, config, pattern:str, latest:bool = False) -> list | None:
		try:
			print(f"get_results: {pattern}")
			if (('host' not in config or config['host'] is None) or
				('port' not in config or config['port'] is None) or
				('user' not in config or config['user'] is None) or
				('password' not in config or config['password'] is None) or
				('directory' not in config or config['directory'] is None)):
				raise ValueError("FTP configuration is incomplete.")
			self.ftp.connect(config['host'], config['port'])
			self.ftp.login(config['user'], config['password'])
			self.ftp.cwd(config['directory'])
			temp = self.bot.get_temp("results")
			# check if storage directory exists and create if not
			files = []
			self.ftp.retrlines("LIST", files.append)
			filenames = [line.split()[-1] for line in files]
			filenames.reverse()
			result = []
			for filename in filenames:
				if not re.match(pattern, filename):
					continue
				if latest and len(result) > 0:
					break
				local_filename = Dest.join(temp, filename)
				result.append(local_filename)
				if not Dest.exists(local_filename):
					with open(local_filename, "wb") as file:
						self.ftp.retrbinary(f"RETR {filename}",
							file.write
						)
			self.ftp.quit()
			return result
		except Exception as e:
			self.bot.debug(e)
			raise e

	def load_result(self, filename:str) -> dict:
		try:
			print(f"load_result: {filename}")
			data = Dest.json.load(filename)
			drivers = []
			cars = {}
			positions = []
			fastest = {}
			session_laps = 0
			session_time = 0
			if len(data["sessionResult"]["leaderBoardLines"]) > 0:
				fastest = {
					"car": 0,
					"driver": 0,
					"lap": 0,
					"time": data["sessionResult"]["bestlap"],
				}
				for position in data["sessionResult"]["leaderBoardLines"]:
					carId = position["car"]["carId"]
					car = {
						"number": position["car"]["raceNumber"],
						"car": position["car"]["carModel"],
						"cup": position["car"]["cupCategory"],
						"group": position["car"]["carGroup"],
						"team": position["car"]["teamName"],
						"laps": 0,
						"time": 0,
						"best": {
							"lap": position["timing"]["lapCount"] - 1, # -1 for formation lap
							"time": position["timing"]["bestLap"],
							"splits": position["timing"]["bestSplits"],
						},
						"drivers": {},
					}
					if len(position["car"]["drivers"]) > 0:
						idx = 0
						for driver in position["car"]["drivers"]:
							car["drivers"][idx] = {
								"playerId": driver["playerId"],
								"firstName": driver["firstName"],
								"lastName": driver["lastName"],
								"shortName": driver["shortName"],
								"laps": [],
								"time": 0,
								"best": {
									"fastest": False,
									"lap": 0,
									"time": 0,
									"splits": [
										0,
										0,
										0
									]
								},
								"penalties": []
							}
							drivers.append({
								"carId": carId,
								"idx": idx,
							})
							idx += 1
					cars[carId] = car
					positions.append({
						"carId": carId,
						"laps": position["timing"]["lapCount"] - 1, # -1 for formation lap
						"time": position["timing"]["totalTime"],
					})
					# update car total time
					if session_time == 0:
						session_time = position["timing"]["totalTime"]
					# update car total laps
					if session_laps == 0:
						session_laps = position["timing"]["lapCount"] - 1 # -1 for formation lap
			if len(data["laps"]):
				#lap = 0
				carLaps = {}
				for l in data["laps"]:
					carId = l["carId"]
					if carId not in carLaps:
						carLaps[carId] = 0
					driverIdx = l["driverIndex"]
					if carId in cars:
						carLaps[carId] += 1
						car = cars[carId]
						car["laps"] += 1
						car["time"] += l["laptime"]
						if driverIdx in car["drivers"]:
							driver = car["drivers"][driverIdx]
							#driver["laps"] += 1
							driver["laps"].append(l["laptime"])
							if l["isValidForBest"] and\
								(
									driver["best"]["time"] == 0 or
									l["laptime"] < driver["best"]["time"]
								):
								driver["best"]["lap"] = carLaps[carId]
								driver["best"]["time"] = l["laptime"]
								if fastest["time"] == l["laptime"]:
									fastest["car"] = carId
									fastest["driver"] = driverIdx
									fastest["lap"] = carLaps[carId] - 1
									driver["best"]["fastest"] = True
							for i, s in enumerate(l["splits"]):
								if driver["best"]["splits"][i] == 0:
									driver["best"]["splits"][i] = s
								elif s < driver["best"]["splits"][i]:
									driver["best"]["splits"][i] = s
							driver["time"] += l["laptime"]
					#lap += 1
			if len(data["penalties"]):
				for p in data["penalties"]:
					carId = p["carId"]
					driverIdx = p["driverIndex"]
					if carId in cars:
						car = cars[carId]
						if driverIdx in car["drivers"]:
							driver = car["drivers"][driverIdx]
							driver["penalties"].append({
								"reason": p["reason"],
								"penalty": p["penalty"],
								"value": p["penaltyValue"],
								"violated": p["violationInLap"],
								"cleared": p["clearedInLap"],
							})
			if len(data["post_race_penalties"]):
				for p in data["post_race_penalties"]:
					carId = p["carId"]
					driverIdx = p["driverIndex"]
					if carId in cars:
						car = cars[carId]
						if driverIdx in car["drivers"]:
							driver = car["drivers"][driverIdx]
							driver["penalties"].append({
								"reason": p["reason"],
								"penalty": p["penalty"],
								"value": p["penaltyValue"],
								"violated": p["violationInLap"],
								"cleared": p["clearedInLap"],
							})
			return {
				"server": data["serverName"],
				"track": data["trackName"],
				"type": data["sessionType"],
				"typeName": {
					"FP": "Free Practice",
					"Q": "Qualifying",
					"R": "Race",
				}.get(data["sessionType"], "Unknown"),
				"wet": data["sessionResult"]["isWetSession"],
				"session": {
					"laps": session_laps,
					"time": session_time,
				},
				"cars": cars,
				"drivers": drivers,
				"positions": positions,
				"fastest": fastest,
				"laps": data["laps"],
			}
		except Exception as e:
			self.bot.debug(e)
			raise e

	async def handle_result(self, ctx:commands.Context, file:str, date:datetime) -> None:
		try:
			print(f"handle_result: {file}")
			data = self.load_result(file)
			if data is None:
				raise ValueError("Error loading result.")
			if len(data['laps']) > 0:
				# save the result
				Dest.json.save(
					Dest.join(
						self.bot.get_temp('results'),
						Dest.suffix(file, '.result')
					),
					data
				)
			track = ACC.fullTrackName(data["track"])
			if len(data["laps"]) == 0:
				embed = self.bot.embed(
					ctx = ctx,
					title = f"{data['server']} · {date.strftime('%d %B %Y')} ***` {data['typeName']} `***",
					description = f"**{track}** · **No laps**",
					bot = True,
				)
				embed.set_footer(
					text = f"Powered by {self.bot.__POWERED_BY__}",
				)
				return await ctx.send(
					embed = embed
				)
			embed = self.bot.embed(
				ctx = ctx,
				title = f"{data['server']} · {date.strftime('%d %B %Y')}   ***` {data['typeName']} `***",
				description = f"**{track}** · **{data['session']['laps']} laps** in **{ACC.convert_time(data['session']['time'])}** {' · ( 🌧️ )' if data['wet'] == 1 else ''}",
				bot = True,
			)
			place = 1
			driver_penalties = []
			# race
			if data["type"] == "R":
				for position in data["positions"]:
					car = data["cars"][position["carId"]]
					drivers = []
					for driver in car["drivers"].values():
						drivers.append(
							f"**{ACC.driverName(driver)}**"
						)
						if len(driver["penalties"]):
							driver_penalties.append(
								{
									"car": {
										"number": car["number"],
										"car": car["car"],
										"group": car["group"],
										"team": car["team"],
									},
									"driver": {
										"playerId": driver["playerId"],
										"firstName": driver["firstName"],
										"lastName": driver["lastName"],
										"shortName": driver["shortName"],
									},
									"penalties": driver["penalties"],
								}
							)
					drivers = ", ".join(drivers)
					inline = (place > 3)
					if place == 1:
						leader = position
						embed.add_field(
							name = f"{ACC.place(place, True)} #{car['number']} {ACC.car(car['car'])[0]} {car['team']}",
							value = f"{drivers}   {ACC.convert_time(position['time'])}",
							inline = inline,
						)
					else:
						if position["laps"] < leader["laps"]:
							delta = leader["laps"] - position["laps"]
							embed.add_field(
								name = f"{ACC.place(place, True)} #{car['number']} {ACC.car(car['car'])[0]}",
								#value = f"{drivers} - {self.convert_time(position['time'])} (+{delta} laps)",
								value = f"{drivers}   +{delta} lap{delta > 1 and 's' or ''}",
								inline = inline,
							)
						else:
							delta = position["time"] - leader["time"]
							embed.add_field(
								name = f"{ACC.place(place, True)} #{car['number']} {ACC.car(car['car'])[0]}",
								value = f"{drivers} · {ACC.convert_time(position['time'])} · (+{ACC.convert_time(delta)})",
								inline = inline,
							)
					place += 1
			# free practice or qualifying
			if data["type"] in ["FP", "Q"]:
				# show fastest lap and most laps
				for position in data["positions"]:
					car = data["cars"][position["carId"]]
					drivers = []
					best_time = 0
					best_time_str = "N/A"
					for driver in car["drivers"].values():
						#print(f"driver: {driver['best']['time']}")
						# find the driver with the fastest best lap
						if best_time == 0:
							best_time = driver["best"]["time"]
							best_lap = driver["best"]["lap"]
						if driver["best"]["time"] < best_time:
							best_time = driver["best"]["time"]
							best_lap = driver["best"]["lap"]
							fastestDriver = driver
						drivers.append(
							f"**{ACC.driverName(driver)}**"
						)
					drivers = ", ".join(drivers)
					if car["laps"] == 0:
						best_time_str = "N/A"
					else:
						best_time_str = ACC.convert_time(best_time)
					inline = True
					embed.add_field(
						name = f"{ACC.place(place)} #{car['number']} {ACC.car(car['car'])[0]} {car['team']}",
						value = f"{drivers} · {best_time_str} on lap {best_lap} · ({position['laps']} lap{position['laps'] > 1 and 's' or ''})",
						inline = inline,
					)
					place += 1
			# show fastest lap

			fastestDriver = f"**{ACC.driverName(data['cars'][data['fastest']['car']]['drivers'][data['fastest']['driver']])}**"
			embed.add_field(
				name = "Fastest Lap",
				value = f"**🛞 #{data['cars'][data['fastest']['car']]['number']}** {fastestDriver}"\
						f" · {ACC.convert_time(data['fastest']['time'])} on lap {data['fastest']['lap']}",
				inline = False,
			)
			# show penalties
			if len(driver_penalties):
				embed.add_field(
					name = "\u200b",
					value = "**Penalties**",
					inline = False,
				)
				for pen in driver_penalties:
					for penalty in pen["penalties"]:
						if penalty["penalty"] == "None":
							continue
						if penalty["violated"] == 0:
							continue
						cleared = f"Cleared on lap {penalty['cleared']}" if penalty["cleared"] >= penalty["violated"] else "**Not Cleared**"
						embed.add_field(
							name = f"⚠️ #{pen['car']['number']} {ACC.car(pen['car']['car'])[0]} · **{ACC.driverName(pen['driver'])}**",
							value = f"Lap {penalty['violated']} · {penalty['reason']} · {penalty['penalty']} · {cleared}",
							inline = False,
						)
			embed.set_footer(
				text = f"Powered by {self.bot.__POWERED_BY__}",
			)
			return await ctx.send(
				content = f"🏎️",
				embed = embed,
			)
		except Exception as e:
			raise e

	async def handle_request(self, ctx:commands.Context, session:str, date:str = None, time:str = None) -> None:
		try:
			print(f"handle_request: {session} {date} {time}")
			async with ctx.typing():
				config = self.bot.get_config(ctx.guild, "connect", "acc")
				latest = False
				if config is None:
					raise ValueError("ACC Dedicated Server configuration not found.")
				if session not in ["FP", "Q", "R"]:
					raise ValueError("Session must be one of **FP**, **Q**, **R**.")
				if date is None or date == "" or date.lower() == "latest":
					print("latest")
					date = ACC.parse_date_for_regexp(date)
					date_str = "latest"
					time = ACC.parse_time_for_regexp(time)
					time_str = "latest"
					latest = True
				elif date == "*":
					print("list")
					date = r"\d{6}"
					date_str = "list"
					time = r"\d{6}"
					time_str = "list"
					latest = False
				else:
					print(f"not latest")
					date = ACC.parse_date_for_regexp(date)
					date_str = datetime.strptime(date, "%y%m%d").strftime("%d %B %Y")
					if time is None or time == "latest":
						time = r"\d{6}"
						time_str = "latest"
						latest = True
					elif time == '*':
						time = r"\d{6}"
						time_str = "list"
						latest = False
					else:
						time = ACC.parse_time_for_regexp(time)
						time_str = time
				pattern = f"{date}_{time}_{session}.json"
				results = self.get_results(config, pattern, latest)
				if results is None:
					embed = self.bot.embed(
						ctx = ctx,
						title = "Error",
						description = "No results found.",
						bot = True,
					)
					embed.set_footer(
						text = f"Powered by {self.bot.__POWERED_BY__}",
					)
					return await ctx.send(
						embed = embed
					)
				if len(results) == 0:
					embed = self.bot.embed(
						ctx = ctx,
						title = "Error",
						description = f"No results found for **{session}** on **{date_str}** at **{time_str}**.",
						bot = True,
					)
					embed.set_footer(
						text = f"Powered by {self.bot.__POWERED_BY__}",
					)
					return await ctx.send(
						embed = embed
					)
				if len(results) > 1:
					dates = {}
					for result in results:
						date, time, _ = Dest.filename(result).split("_")
						# build the dates dictionary and add the time
						if date not in dates:
							dates[date] = []
						dates[date].append(time)
					embed = self.bot.embed(
						ctx = ctx,
						title = f"Multiple results found for **{session}** on **{date_str}** at **{time_str}**.",
						description = f"Please select one of the following date(s) & times",
						bot = True,
					)
					if len(dates) > 10:
						dates = dict(list(dates.items())[:10])
					for date, times in dates.items():
						embed.add_field(
							name = f"{date}",
							value = f"{' '.join(times)}",
							inline = False,
						)
					embed.set_footer(
						text = f"Powered by {self.bot.__POWERED_BY__}",
					)
					return await ctx.send(
						embed = embed
					)
				# extract date & time from filename and convert to datetime yymmdd_hhmmss
				date, time, _ = Dest.filename(results[0]).split("_")
				date = datetime.strptime(f"{date}{time}", "%y%m%d%H%M%S")
				#print(f"date: {date}")
				return await self.handle_result(
					ctx = ctx,
					file = results[0],
					date = date,
				)
		except ValueError as e:
			traceback.print_exc()
			raise e
		except Exception as e:
			traceback.print_exc()
			raise e

	@commands.command(
		description = "Get the results of the date",
		usage = "race [date] [time]",
		hidden = False,
		aliases = [
			"r",
			"result",
			"race_results",
		]
	)
	@commands.guild_only()
	async def race(self, ctx:commands.Context, date:str = None, time:str = None) -> None:
		"""
		Get the race results of the date
		```
		{ctx.prefix}race 241231 235959
		{ctx.prefix}race latest
		{ctx.prefix}race yesterday latest
		```
		"""
		try:
			print(f"race")
			await self.handle_request(
				ctx = ctx,
				session = "R",
				date = date,
				time = time,
			)
		except ValueError as e:
			await self.bot.warn(
				e,
				ctx = ctx,
			)
		except Exception as e:
			traceback.print_exc()
			await self.bot.error(
				e,
				ctx = ctx,
			)

	@commands.command(
		description = "Get the results of the date",
		usage = "qualify [date] [time]",
		hidden = False,
		aliases = [
			"q",
			"qual",
			"quali",
			"qualifying",
			"qualifying_results",
		],
	)
	@commands.guild_only()
	async def qualify(self, ctx:commands.Context, date:str = None, time:str = None) -> None:
		"""
		Get the qualifying results of the date
		```
		{ctx.prefix}qualify 241231 235959
		{ctx.prefix}qualify latest
		{ctx.prefix}qualify yesterday latest
		```
		"""
		try:
			print(f"qualify")
			await self.handle_request(
				ctx = ctx,
				session = "Q",
				date = date,
				time = time,
			)
		except ValueError as e:
			await self.bot.warn(
				e,
				ctx = ctx,
			)
		except Exception as e:
			await self.bot.error(
				e,
				ctx = ctx,
			)

	@commands.command(
		description = "Get the results of the date",
		usage = "practice [date] [time]",
		hidden = False,
		aliases = [
			"f",
			"fp",
			"free",
			"free_practice",
			"practice_results",
		],
	)
	@commands.guild_only()
	async def practice(self, ctx:commands.Context, date:str = None, time:str = None) -> None:
		"""
		Get the practice results of the date
		```
		{ctx.prefix}practice 241231 235959
		{ctx.prefix}practice latest
		{ctx.prefix}practice yesterday latest
		```
		"""
		try:
			print(f"practice")
			await self.handle_request(
				ctx = ctx,
				session = "FP",
				date = date,
				time = time,
			)
		except ValueError as e:
			await self.bot.warn(
				e,
				ctx = ctx,
			)
		except Exception as e:
			await self.bot.error(
				e,
				ctx = ctx,
			)

	@commands.command(
		description = "Clean up the FTP from empty result files",
		usage = "clean",
		hidden = False,
	)
	@commands.guild_only()
	@commands.is_owner()
	@commands.has_permissions(moderate_members=True)
	async def cleanupemptyresults(self, ctx:commands.Context) -> None:
		"""
		Clean up the FTP from empty result files
		```
		{ctx.prefix}clean
		```
		"""
		try:
			print(f"cleanupemptyresults")
			config = self.bot.get_config(ctx.guild, "connect", "acc")
			if config is None:
				raise ValueError("ACC Dedicated Server configuration not found.")
			self.ftp.connect(config['host'], config['port'])
			self.ftp.login(config['user'], config['password'])
			self.ftp.cwd(config['directory'])
			storage = self.bot.get_temp("results_backup")
			files = []
			self.ftp.retrlines("LIST", files.append)
			filenames = [line.split()[-1] for line in files]
			#filenames.reverse()
			print(f"filenames: {filenames}")
			delete_files = []
			for filename in filenames:
				local_filename = Dest.join(storage, filename)
				if not Dest.exists(local_filename):
					with open(local_filename, "wb") as file:
						self.ftp.retrbinary(f"RETR {filename}",
							file.write
						)
				# open the file as json
				data = Dest.json.load(local_filename)
				# check if the file is empty
				if len(data["sessionResult"]["leaderBoardLines"]) == 0:
					r = self.ftp.delete(filename)
					print(f"delete: {filename} {r}")
					#exit()
					# rename local file to .backup.json
					Dest.rename(local_filename, Dest.backup(local_filename))
					print(f"empty: {filename}")
					delete_files.append(filename)
			self.ftp.quit()
			embed = self.bot.embed(
				ctx = ctx,
				title = "Cleanup",
				description = f"{len(delete_files)} empty results have been removed.",
				bot = True,
			)
			embed.set_footer(
				text = f"Powered by {self.bot.__POWERED_BY__}",
			)
			return await ctx.send(
				embed = embed
			)
		except ValueError as e:
			await self.bot.warn(
				e,
				ctx = ctx,
			)
		except Exception as e:
			await self.bot.error(
				e,
				ctx = ctx,
			)



async def setup(bot:commands.Bot) -> None:
	try:
		await bot.add_cog(
			ACCRace(
				bot
			)
		)
	except Exception as e:
		raise e

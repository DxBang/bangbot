"""
Login to ACC Dedicated Server via FTP and get the race results.
"""
import bang
import ftplib
from datetime import datetime
import re
#from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands
#from discord import app_commands
from bang.dest import Dest
from bang.acc import ACC
from bang.human import Human
import traceback


class ACCRace(commands.Cog, name="Race Results"):
	__slots__ = (
		"bot",
		"ftp",
	)
	def __init__(self, bot:bang.Bot) -> None:
		try:
			self.bot = bot
			self.ftp = ftplib.FTP()
		except Exception as e:
			raise e

	def getResults(self, config, pattern:str, latest:bool = False) -> list | None:
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
			temp = self.bot.getTemp("results")
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

	async def sync_results(self, config) -> tuple[list, list]:
		if (('host' not in config or config['host'] is None) or
			('port' not in config or config['port'] is None) or
			('user' not in config or config['user'] is None) or
			('password' not in config or config['password'] is None) or
			('directory' not in config or config['directory'] is None)):
			raise ValueError("FTP configuration is incomplete.")
		print(f"sync_results: {config}")
		temp = self.bot.getTemp("results")
		self.ftp.connect(config['host'], config['port'])
		self.ftp.login(config['user'], config['password'])
		self.ftp.cwd(config['directory'])
		files = []
		download_files = []
		delete_files = []
		self.ftp.retrlines("LIST", files.append)
		filenames = [line.split()[-1] for line in files]
		for filename in filenames:
			local_filename = Dest.join(temp, filename)
			if not Dest.exists(local_filename):
				print(f"download: {filename}")
				with open(local_filename, "wb") as file:
					self.ftp.retrbinary(f"RETR {filename}",
						file.write
					)
					download_files.append(filename)
			data = Dest.json.load(local_filename)
			if len(data["laps"]) == 0:
				print(f"delete: {filename}")
				if not Dest.exists(Dest.backup(local_filename)):
					Dest.rename(
						local_filename,
						Dest.backup(local_filename)
					)
				else:
					Dest.remove(
						local_filename
					)
				delete_files.append(filename)
				#self.ftp.delete(filename)
		self.ftp.quit()
		return download_files, delete_files

	def loadResult(self, file:str) -> dict:
		try:
			print(f"loadResult: {file}")
			#converted_file = Dest.suffix(file, ".result")
			#if Dest.exists(converted_file):
			#	print(f"converted_file: {converted_file}")
			#	return ACC.load(converted_file)
			if not Dest.exists(file):
				raise ValueError(f"File not found: {file}")
			return ACC.loadSessionResult(file)
		except Exception as e:
			self.bot.debug(e)
			raise e

	async def handleResult(self, ctx:commands.Context, data:dict, date:datetime) -> None:
		try:
			# read the result file: tmp/results/240309_220433_R.result.json
			session = data.get("session", {})
			cars = data.get("cars", {})
			laps = data.get("laps", {})
			positions = data.get("positions", {})
			if len(data.get("laps")) == 0:
				embed = self.bot.embed(
					ctx = ctx,
					title = f"{session['name']} · {date.strftime('%d %B %Y')}  ***` {session['type']['name']} `***",
					description = f"**{session['track']['name']}** · **No laps**",
					bot = True,
				)
				embed.set_footer(
					text = self.bot.__POWERED_BY__,
				)
				return await ctx.send(
					embed = embed
				)
			embed = self.bot.embed(
				ctx = ctx,
				title = f"{session['name']} · {date.strftime('%d %B %Y')}   ***` {session['type']['name']} `***",
				description = f"**{session['track']['name']}** · **{session['laps']} laps** in **{ACC.convertTime(session['time'])}** {' · ( 🌧️ )' if session['wet'] == 1 else ''}",
				bot = True,
			)
			place = 1
			# race
			if session["type"]["tag"] == "R":
				for position in positions:
					car = cars.get(position["carId"])
					drivers = []
					for driver in car["drivers"]:
						drivers.append(
							f"**{ACC.driverName(driver)}**"
						)
					drivers = ", ".join(drivers)
					inline = (place > 3)
					if place == 1:
						leader = position
						embed.add_field(
							name = f"{ACC.place(place, True)} #{car['number']} {car['model']['name']} {car['team']}",
							value = f"{drivers}   {ACC.convertTime(position['timing']['time'])}",
							inline = inline,
						)
					else:
						if position["timing"]["laps"] < leader["timing"]["laps"]:
							delta = leader["timing"]["laps"] - position["timing"]["laps"]
							embed.add_field(
								name = f"{ACC.place(place, True)} #{car['number']} {car['model']['name']}",
								#value = f"{drivers} - {self.convertTime(position['time'])} (+{delta} laps)",
								value = f"{drivers}   +{delta} lap{delta > 1 and 's' or ''}",
								inline = inline,
							)
						else:
							delta = position["timing"]["time"] - leader["timing"]["time"]
							embed.add_field(
								name = f"{ACC.place(place, True)} #{car['number']} {car['model']['name']}",
								value = f"{drivers} · {ACC.convertTime(position['timing']['time'])} · (+{ACC.convertTime(delta)})",
								inline = inline,
							)
					place += 1
			# free practice or qualifying
			elif session["type"]["tag"] in ["FP", "Q"]:
				# show fastest lap and most laps
				for position in positions:
					inline = True #(place > 3)
					car = cars.get(position["carId"])
					drivers = []
					best_lap = 0
					best_time = position["timing"]["best"]["lap"]
					best_driver = None
					for _lap, lap in enumerate(laps):
						for _car in lap:
							if _car["carId"] == position["carId"]:
								if _car["time"] == best_time:
									best_lap = _lap + 1
									best_driver = car["drivers"][_car["driverId"]]
									# break both loops
									break
						else:
							continue
						break
					for driver in car["drivers"]:
						drivers.append(
							f"**{ACC.driverName(driver)}**"
						)
					drivers = ", ".join(drivers)
					if position["timing"]["laps"] == 0:
						embed.add_field(
							name = f"{ACC.place(place)} #{car['number']} {car['model']['name']} {car['team']}",
							value = f"{drivers} · no time set · (0 laps)",
							inline = inline,
						)
					elif best_driver is not None:
						best_driver = f"**{ACC.driverName(best_driver)}**"
						best_time = ACC.convertTime(best_time)
						embed.add_field(
							name = f"{ACC.place(place)} #{car['number']} {car['model']['name']} {car['team']}",
							value = f"{best_driver} · {best_time} on lap {best_lap} · ({position['timing']['laps']} lap{position['timing']['laps'] > 1 and 's' or ''})",
							inline = inline,
						)
					place += 1
			# show fastest lap
			if session['best']['lap']['driver'] is not None:
				bestLap = session['best']['lap']
				bestCar = cars.get(bestLap['carId'])
				bestDriver = f"**{ACC.driverName(bestCar.get('drivers')[bestLap['driverId']])}**"
				embed.add_field(
					name = "Fastest Lap",
					value = f"**🛞 #{bestCar['number']}** {bestDriver}"\
							f" · {ACC.convertTime(bestLap['time'])} on lap {bestLap['lap']}",
					inline = False,
				)
			# show penalties
			_types = (
				"race",
				"post",
			)
			for _type in _types:
				penalties = data.get("penalties").get(_type, {})
				if len(penalties) == 0:
					continue
				embed.add_field(
					name = "\u200b",
					value = f"**Penalties**" if _type == "race" else f"**Post Race Penalties**",
					inline = False,
				)
				for carId, _penalties in penalties.items():
					car = cars.get(carId)
					for penalty in _penalties:
						#if penalty['violated'] == 0:
						#	continue
						# get the lap from the penalty["violated"] (which is the lap the penalty was given)
						lap = laps[penalty["violated"]]
						for _car in lap:
							if _car["carId"] == carId:
								# get the driver from the carId and the driverId
								driver = cars.get(carId).get("drivers")[
									_car["driverId"]
								]
								break
						embed.add_field(
							name = f"⚠️ #{car['number']} {car['model']['name']} · **{ACC.driverName(driver)}**",
							value = f"Lap {penalty['violated']} · {penalty['reason']} · {penalty['penalty']} · {penalty['value']} · {'cleared' if penalty['cleared'] > 0 else 'not cleared'}",
							inline = False,
						)
			embed.set_footer(
				text = self.bot.__POWERED_BY__,
			)
			return await ctx.send(
				content = f"🏎️",
				embed = embed,
			)
		except Exception as e:
			raise e

	async def handleRequest(self, ctx:commands.Context, session:str, date:datetime = None, time:datetime = None, sync:bool = False) -> None:
		try:
			print(f"handleRequest: {session} {date} {time}")
			async with ctx.typing():
				config = self.bot.getConfig(ctx.guild, "connect", "acc")
				latest = False
				if config is None:
					raise ValueError("ACC Dedicated Server configuration not found.")
				if session.lower() not in ["fp", "q", "r"]:
					raise ValueError("Session must be one of **FP**, **Q**, **R**.")
				temp = self.bot.getTemp("results")
				if sync:
					await self.sync_results(self.bot.getConfig(ctx.guild, "connect", "acc"))

				if session.lower() == "r":
					file = Dest.join(
						temp,
						ACC.sessionRaceFile(temp, date, time)
					)
				elif session.lower() == "q":
					file = Dest.join(
						temp,
						ACC.sessionQualifyingFile(temp, date, time)
					)
				elif session.lower() == "fp":
					file = Dest.join(
						temp,
						ACC.sessionFreePracticeFile(temp, date, time)
					)
				else:
					raise ValueError("Invalid session.")
				print(f"file: {file}")
				data = ACC.loadSessionResult(file)
				if len(data.get("laps", [])) == 0:
					embed = self.bot.embed(
						ctx = ctx,
						title = "Error",
						description = "No result found.",
						bot = True,
					)
					embed.set_footer(
						text = self.bot.__POWERED_BY__,
					)
					return await ctx.send(
						embed = embed
					)

				# extract date & time from filename and convert to datetime yymmdd_hhmmss
				date, time, _ = Dest.filename(file).split("_")
				date = datetime.strptime(f"{date}{time}", "%y%m%d%H%M%S")
				#print(f"date: {date}")
				return await self.handleResult(
					ctx = ctx,
					data = data,
					date = date,
				)
		except ValueError as e:
			traceback.print_exc()
			raise e
		except Exception as e:
			traceback.print_exc()
			raise e

	async def handleList(self, ctx:commands.Context, session:str, date:str, time:str, sync:bool = False) -> None:
		try:
			if session.lower() not in ["fp", "q", "r"]:
				raise ValueError("Session must be one of **FP**, **Q**, **R**.")
			if date == "*":
				# show ALL
				date = None
			else:
				date = Human.date(date)
				if time == "*":
					# show ALL of the day
					time = None
			files = ACC.sessionTimestampFiles(
				self.bot.getTemp("results"),
			)
			if session.lower() == "r":
				files = files.get("r")
			elif session.lower() == "q":
				files = files.get("q")
			elif session.lower() == "fp":
				files = files.get("fp")
			if len(files) == 0:
				embed = self.bot.embed(
					ctx = ctx,
					title = "Results",
					description = "No results found.",
					bot = True,
				)
				embed.set_footer(
					text = self.bot.__POWERED_BY__,
				)
				return await ctx.send(
					embed = embed
				)
			# sort reverse the files list
			_dates = {}
			results = 0
			for timestamp in sorted(files.keys(), reverse=True):
				_date = datetime.fromtimestamp(timestamp)
				if date is not None:
					if _date.date() != date.date():
						continue
				if _date.strftime("%y%m%d") not in _dates:
					_dates[_date.strftime("%y%m%d")] = []
				_dates[_date.strftime("%y%m%d")].append(_date.strftime("%H%M%S"))
				results += 1
			embed = self.bot.embed(
				ctx = ctx,
				title = "Results",
				description = f"{results} results found.",
				bot = True,
			)
			embed.set_footer(
				text = self.bot.__POWERED_BY__,
			)
			limit = 15
			for _date, _time in _dates.items():
				if limit == 0:
					break
				embed.add_field(
					name = f"{_date}",
					# separate the times with a newline
					value = "\n".join(_time),
					inline = True,
				)
				limit -= 1
			return await ctx.send(
				embed = embed
			)

		except Exception as e:
			traceback.print_exc()
			raise e

	@commands.command(
		description = "Get the results of the date",
		usage = "race [date] [time]",
		hidden = True,
		aliases = [
			"r",
			"result",
			"race_results",
		]
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def race(self, ctx:commands.Context, *, input:str = None) -> None:
		"""
		Get the race results of the date
		```
		{ctx.prefix}race 241231 235959
		{ctx.prefix}race latest
		{ctx.prefix}race yesterday latest
		```
		"""
		try:
			date, time, _, _, _, sync = ACC.parseRaceInput(input)
			if date == '*' or time == '*':
				return await self.handleList(
					ctx = ctx,
					session = "r",
					date = date,
					time = time,
					sync = sync,
				)
			print(f"race: {date} {time} {sync}")
			await self.handleRequest(
				ctx = ctx,
				session = "r",
				date = ACC.parseDate(date),
				time = ACC.parseTime(time),
				sync = Human.parseBool(sync),
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
		hidden = True,
		aliases = [
			"q",
			"qual",
			"quali",
			"qualifying",
			"qualifying_results",
		],
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def qualify(self, ctx:commands.Context, *, input:str = None) -> None:
		"""
		Get the qualifying results of the date
		```
		{ctx.prefix}qualify 241231 235959
		{ctx.prefix}qualify latest
		{ctx.prefix}qualify yesterday latest
		```
		"""
		try:
			date, time, _, _, _, sync = ACC.parseRaceInput(input)
			if date == '*' or time == '*':
				return await self.handleList(
					ctx = ctx,
					session = "q",
					date = date,
					time = time,
					sync = sync,
				)
			print(f"qualify: {date} {time} {sync}")
			await self.handleRequest(
				ctx = ctx,
				session = "q",
				date = ACC.parseDate(date),
				time = ACC.parseTime(time),
				sync = Human.parseBool(sync),
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
		usage = "practice [date] [time]",
		hidden = True,
		aliases = [
			"f",
			"fp",
			"free",
			"free_practice",
			"practice_results",
		],
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def practice(self, ctx:commands.Context, *, input:str = None) -> None:
		"""
		Get the practice results of the date
		```
		{ctx.prefix}practice 241231 235959
		{ctx.prefix}practice latest
		{ctx.prefix}practice yesterday latest
		```
		"""
		try:
			date, time, _, _, _, sync = ACC.parseRaceInput(input)
			if date == '*' or time == '*':
				return await self.handleList(
					ctx = ctx,
					session = "fp",
					date = date,
					time = time,
					sync = sync,
				)
			print(f"practice: {date} {time} {sync}")
			await self.handleRequest(
				ctx = ctx,
				session = "fp",
				date = ACC.parseDate(date),
				time = ACC.parseTime(time),
				sync = Human.parseBool(sync),
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
		description = "Create a session",
		usage = "create [session] [number of races]",
		hidden = True,
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def create(self, ctx:commands.Context, session:str, races:int = 1) -> None:
		"""
		Create a session
		```
		{ctx.prefix}create S1 10
		{ctx.prefix}create S2 12
		{ctx.prefix}create "Special Event" 3
		```
		"""
		try:
			if session is None:
				raise ValueError("Missing a session name.")
			temp = self.bot.getTemp("sessions")
			# create the session
			"""
			session = [
				"241231_235959_R",
				"241231_235959_Q",
				None,
				None,
				None,
				None,
				None,
			]
			"""
			# create the session as a list of None values with the length of races
			session = [None for _ in range(races)]
			# save the session to a file
			Dest.json.save(
				Dest.join(temp, session),
				session
			)
			embed = self.bot.embed(
				ctx = ctx,
				title = "Session",
				description = f"Session **{session}** created.",
				bot = True,
			)
			embed.set_footer(
				text = self.bot.__POWERED_BY__,
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
		description = "The session results",
		usage = "session [session]",
		hidden = True,
		aliases = [
			"all",
		],
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def session(self, ctx:commands.Context, session:str = None) -> None:
		"""
		Get the session results
		```
		{ctx.prefix}session S2
		{ctx.prefix}session q
		{ctx.prefix}session fp
		```
		"""
		try:
			if session is None:
				raise ValueError("Session must be one of **FP**, **Q**, **R**.")
			if session.lower() not in ["fp", "q", "r"]:
				raise ValueError("Session must be one of **FP**, **Q**, **R**.")
			await self.handleList(
				ctx = ctx,
				session = session,
				date = "*",
				time = "*",
				sync = False,
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
		description = "Clean up the FTP from empty result files",
		usage = "clean",
		hidden = True,
	)
	@commands.guild_only()
	@commands.is_owner()
	@commands.has_permissions(moderate_members=True)
	async def cleanupEmptyResults(self, ctx:commands.Context) -> None:
		"""
		Clean up the FTP from empty result files
		```
		{ctx.prefix}cleanupemptyresults
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
			storage = self.bot.getTemp("results_backup")
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
				title = "Cleanup Empty Results",
				description = f"{len(delete_files)} empty results have been removed.",
				bot = True,
			)
			embed.set_footer(
				text = self.bot.__POWERED_BY__,
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

async def setup(bot:bang.Bot) -> None:
	try:
		await bot.add_cog(
			ACCRace(
				bot
			)
		)
	except Exception as e:
		raise e

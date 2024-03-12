"""
Login to ACC Dedicated Server via FTP and get the race results.
"""
import os
#import sys
import json
import ftplib
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta, timezone
import re
import discord
#from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands
from discord import app_commands
from bang.dest import Dest
import traceback

class ACCRace(commands.Cog, name="ACC Dedicated Server"):
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

	def fullTrackName(self, short:str) -> str:
		return {
			"barcelona": "Circuit de Barcelona-Catalunya",
			"barcelona": "Circuit de Barcelona-Catalunya",
			"brands_hatch": "Brands Hatch",
			"cota": "Circuit of the Americas",
			"donington": "Donington Park",
			"hungaroring": "Hungaroring",
			"imola": "Autodromo Internazionale Enzo e Dino Ferrari",
			"indianapolis": "Indianapolis Motor Speedway",
			"kyalami": "Kyalami Grand Prix Circuit",
			"laguna_seca": "WeatherTech Raceway Laguna Seca",
			"misano": "Misano World Circuit",
			"monza": "Autodromo Nazionale Monza",
			"mount_panorama": "Mount Panorama Circuit",
			"nurburgring": "Nürburgring",
			"oulton_park": "Oulton Park",
			"paul_ricard": "Circuit Paul Ricard",
			"silverstone": "Silverstone Circuit",
			"snetterton": "Snetterton Circuit",
			"spa": "Circuit de Spa-Francorchamps",
			"suzuka": "Suzuka International Racing Course",
			"valencia": "Circuit Ricardo Tormo",
			"watkins_glen": "Watkins Glen International",
			"zandvoort": "Circuit Zandvoort",
			"zolder": "Circuit Zolder",
			"monza_2019": "Autodromo Nazionale Monza '19",
			"brands_hatch_2019": "Brands Hatch '19",
			"spa_2019": "Circuit de Spa-Francorchamps '19",
			"misano_2019": "Misano World Circuit '19",
			"paul_ricard_2019": "Circuit Paul Ricard '19",
			"zolder_2019": "Circuit Zolder '19",
			"zandvoort_2019": "Circuit Zandvoort '19",
			"silverstone_2019": "Silverstone Circuit '19",
			"hungaroring_2019": "Hungaroring '19",
			"nurburgring_2019": "Nürburgring '19",
			"barcelona_2019": "Circuit de Barcelona-Catalunya '19",
			"kyalami_2019": "Kyalami Grand Prix Circuit '19",
			"mount_panorama_2019": "Mount Panorama Circuit '19",
			"suzuka_2019": "Suzuka International Racing Course '19",
			"laguna_seca_2019": "WeatherTech Raceway Laguna Seca '19",
			"oulton_park_2019": "Oulton Park '19",
			"snetterton_2019": "Snetterton Circuit '19",
			"donington_2019": "Donington Park '19",
			"monza_2020": "Autodromo Nazionale Monza '20",
			"brands_hatch_2020": "Brands Hatch '20",
			"spa_2020": "Circuit de Spa-Francorchamps '20",
			"misano_2020": "Misano World Circuit '20",
			"paul_ricard_2020": "Circuit Paul Ricard '20",
			"zolder_2020": "Circuit Zolder '20",
			"zandvoort_2020": "Circuit Zandvoort '20",
			"silverstone_2020": "Silverstone Circuit '20",
			"hungaroring_2020": "Hungaroring '20",
			"nurburgring_2020": "Nürburgring '20",
			"barcelona_2020": "Circuit de Barcelona-Catalunya '20",
			"kyalami_2020": "Kyalami Grand Prix Circuit '20",
			"mount_panorama_2020": "Mount Panorama Circuit '20",
			"suzuka_2020": "Suzuka International Racing Course '20",
			"laguna_seca_2020": "WeatherTech Raceway Laguna Seca '20",
			"oulton_park_2020": "Oulton Park '20",
			"snetterton_2020": "Snetterton Circuit '20",
			"donington_2020": "Donington Park '20",
			"imola_2020": "Autodromo Internazionale Enzo e Dino Ferrari '20",
		}.get(short, short)

	def place(self, place:int) -> str:
		return {
			1: "🥇",
			2: "🥈",
			3: "🥉",
			4: "4️⃣",
			5: "5️⃣",
			6: "6️⃣",
			7: "7️⃣",
			8: "8️⃣",
			9: "9️⃣",
			10: "🔟",
			11: "⓫",
			12: "⓬",
			13: "⓭",
			14: "⓮",
			15: "⓯",
			16: "⓰",
			17: "⓱",
			18: "⓲",
			19: "⓳",
			20: "⓴",
			21: "㉑",
			22: "㉒",
			23: "㉓",
			24: "㉔",
			25: "㉕",
			26: "㉖",
			27: "㉗",
			28: "㉘",
			29: "㉙",
			30: "㉚",
			31: "㉛",
			32: "㉜",
			33: "㉝",
			34: "㉞",
			35: "㉟",
			36: "㊱",
			37: "㊲",
			38: "㊳",
			39: "㊴",
			40: "㊵",
			41: "㊶",
			42: "㊷",
			43: "㊸",
			44: "㊹",
			45: "㊺",
			46: "㊻",
			47: "㊼",
			48: "㊽",
			49: "㊾",
			50: "㊿",
		}.get(place, f"{place}.")

	def car(self, car:int) -> dict:
		return {
			0: ["Porsche 991 GT3 R", 2018, "GT3"],
			1: ["Mercedes-AMG GT3", 2015, "GT3"],
			2: ["Ferrari 488 GT3", 2018, "GT3"],
			3: ["Audi R8 LMS", 2015, "GT3"],
			4: ["Lamborghini Huracán GT3", 2015, "GT3"],
			5: ["McLaren 650S GT3", 2015, "GT3"],
			6: ["Nissan GT-R Nismo GT3", 2018, "GT3"],
			7: ["BMW M6 GT3", 2017, "GT3"],
			8: ["Bentley Continental GT3", 2018, "GT3"],
			9: ["Porsche 991 II GT3 Cup", 2017, "GTC"],
			10: ["Nissan GT-R Nismo GT3", 2015, "GT3"],
			11: ["Bentley Continental GT3", 2015, "GT3"],
			12: ["AMR V12 Vantage GT3", 2013, "GT3"],
			13: ["Reiter Engineering R-EX GT3", 2017, "GT3"],
			14: ["Emil Frey Jaguar G3", 2012, "GT3"],
			15: ["Lexus RC F GT3", 2016, "GT3"],
			16: ["Lamborghini Huracán GT3 Evo", 2019, "GT3"],
			17: ["Honda NSX GT3", 2017, "GT3"],
			18: ["Lamborghini Huracán SuperTrofeo", 2015, "GTC"],
			19: ["Audi R8 LMS Evo", 2019, "GT3"],
			20: ["AMR V8 Vantage", 2019, "GT3"],
			21: ["Honda NSX GT3 Evo", 2019, "GT3"],
			22: ["McLaren 720S GT3", 2019, "GT3"],
			23: ["Porsche 911 II GT3 R", 2019, "GT3"],
			24: ["Ferrari 488 GT3 Evo", 2020, "GT3"],
			25: ["Mercedes-AMG GT3", 2020, "GT3"],
			26: ["BMW M4 GT3", 2022, "GT3"],
			27: ["Porsche 992 GT3 Cup", 2022, "GTC"],
			28: ["BMW M2 Club Sport Racing", 2022, "TCX"],
			29: ["Lamborghini Huracán SuperTrofeo EVO2", 2022, "GTC"],
			30: ["Ferrari 488 Challenge Evo", 2022, "GTC"],
			31: ["Audi R8 LMS GT3 Evo 2", 2022, "GT3"],
			32: ["Ferrari 296 GT3", 2023, "GT3"],
			33: ["Lamborghini Huracan GT3 Evo 2", 2023, "GT3"],
			34: ["Porsche 992 GT3 R", 2023, "GT3"],
			35: ["McLaren 720S GT3 Evo", 2023, "GT3"],
			50: ["Alpine A110 GT4", 2018, "GT4"],
			51: ["Aston Martin Vantage GT4", 2018, "GT4"],
			52: ["Audi R8 LMS GT4", 2018, "GT4"],
			53: ["BMW M4 GT4", 2018, "GT4"],
			55: ["Chevrolet Camaro GT4", 2017, "GT4"],
			56: ["Ginetta G55 GT4", 2012, "GT4"],
			57: ["KTM X-Bow GT4", 2016, "GT4"],
			58: ["Maserati MC GT4", 2016, "GT4"],
			59: ["McLaren 570S GT4", 2016, "GT4"],
			60: ["Mercedes AMG GT4", 2016, "GT4"],
			61: ["Porsche 718 Cayman GT4 Clubsport", 2019, "GT4"],
		}.get(car, [f"Unknown Car #{car}", 0, "Unknown"])

	def convert_time(self, ms:int) -> str:
		if ms >= 31536000000:
			return str(datetime.utcfromtimestamp(ms / 1000).strftime("%Yy %mn %dd %H:%M:%S.%f")[:-3])
		if ms >= 86400000:
			return str(datetime.utcfromtimestamp(ms / 1000).strftime("%dd %H:%M:%S.%f")[:-3])
		if ms >= 3600000:
			return str(datetime.utcfromtimestamp(ms / 1000).strftime("%H.%M:%S.%f")[:-3])
		if ms >= 60000:
			return str(datetime.utcfromtimestamp(ms / 1000).strftime("%M:%S.%f")[:-3])
		return str(datetime.utcfromtimestamp(ms / 1000).strftime("%S.%f")[:-3])

	def driverName(self, driver:dict) -> str:
		if driver["firstName"] != "" and driver["lastName"] != "":
			return f"**{driver['firstName']} {driver['lastName']}**"
		elif driver["lastName"] != "":
			return f"**{driver['lastName']}**"
		else:
			return f"**{driver['shortName']}**"

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
			# save the result
			Dest.json.save(
				Dest.join(
					self.bot.get_temp('results'),
					Dest.suffix(file, '.result')
				),
				data
			)
			if data is None:
				raise ValueError("Error loading result.")
			track = self.fullTrackName(data["track"])
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
				description = f"**{track}** · **{data['session']['laps']} laps** in **{self.convert_time(data['session']['time'])}**{' · ( 🌧️ )' if data['wet'] == 1 else ''}",
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
							self.driverName(driver)
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
							name = f"{self.place(place)} #{car['number']} {self.car(car['car'])[0]} {car['team']}",
							value = f"{drivers}   {self.convert_time(position['time'])}",
							inline = inline,
						)
					else:
						if position["laps"] < leader["laps"]:
							delta = leader["laps"] - position["laps"]
							embed.add_field(
								name = f"{self.place(place)} #{car['number']} {self.car(car['car'])[0]}",
								#value = f"{drivers} - {self.convert_time(position['time'])} (+{delta} laps)",
								value = f"{drivers}   +{delta} lap{delta > 1 and 's' or ''}",
								inline = inline,
							)
						else:
							delta = position["time"] - leader["time"]
							embed.add_field(
								name = f"{self.place(place)} #{car['number']} {self.car(car['car'])[0]}",
								value = f"{drivers} · {self.convert_time(position['time'])} · (+{self.convert_time(delta)})",
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
							self.driverName(driver)
						)
					drivers = ", ".join(drivers)
					if car["laps"] == 0:
						best_time_str = "N/A"
					else:
						best_time_str = self.convert_time(best_time)
					embed.add_field(
						name = f"{self.place(place)} #{car['number']} {self.car(car['car'])[0]} {car['team']}",
						value = f"{drivers} · {best_time_str} on lap {best_lap} · ({position['laps']} lap{position['laps'] > 1 and 's' or ''})",
						inline = False,
					)
					place += 1
			# show fastest lap

			fastestDriver = self.driverName(data['cars'][data['fastest']['car']]['drivers'][data['fastest']['driver']])
			embed.add_field(
				name = "Fastest Lap",
				value = f"**🛞 #{data['cars'][data['fastest']['car']]['number']}** {fastestDriver}"\
						f" · {self.convert_time(data['fastest']['time'])} on lap {data['fastest']['lap']}",
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
							name = f"⚠️ #{pen['car']['number']} {self.car(pen['car']['car'])[0]} · {self.driverName(pen['driver'])}",
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
					date = self.parse_date(date)
					date_str = "latest"
					time = self.parse_time(time)
					time_str = "latest"
					latest = True
				else:
					print("not latest")
					date = self.parse_date(date)
					date_str = datetime.strptime(date, "%y%m%d").strftime("%d %B %Y")
					if time is None or time == "latest":
						time = r"\d{6}"
						time_str = "latest"
						latest = True
					if time == '*':
						time = r"\d{6}"
						time_str = "list"
						latest = False
					else:
						time = self.parse_time(time)
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
					times = []
					for result in results:
						_, time, _ = Dest.filename(result).split("_")
						times.append(
							time
						)
					embed = self.bot.embed(
						ctx = ctx,
						title = f"Multiple results found for **{session}** on **{date_str}** at **{time_str}**.",
						description = f"Please select one of the following times:\n\n{', '.join(times)}",
						bot = True,
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

	def parse_date(self, date:str, throw:bool = True) -> str | None:
		if date is None or date.lower() == "latest":
			return "\d{6}"
		if date.lower() == "today":
			return datetime.now(timezone.utc).strftime("%y%m%d")
		if date.lower() == "yesterday":
			return (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%y%m%d")
		if re.match(r"^[0-9]{2}[0-1][0-9][0-3][0-9]$", date):
			return datetime.strptime(date, "%y%m%d").strftime("%y%m%d")
		if re.match(r"^[1-2][0-9][0-9]{2}[0-1][0-9][0-3][0-9]$", date):
			return datetime.strptime(date, "%Y%m%d").strftime("%y%m%d")
		if re.match(r"^[0-9]{4}-[0-1]?[0-9]-[0-3]?[0-9]$", date):
			return datetime.strptime(date, "%Y-%m-%d").strftime("%y%m%d")
		if re.match(r"^[0-3]?[0-9]/[0-1]?[0-9]/[0-9]{2}$", date):
			return datetime.strptime(date, "%d/%m/%y").strftime("%y%m%d")
		if re.match(r"^[0-3]?[0-9]/[0-1]?[0-9]/[0-9]{4}$", date):
			return datetime.strptime(date, "%d/%m/%Y").strftime("%y%m%d")
		if throw:
			raise ValueError("Invalid date format. Try **YYMMDD**, **YYYYMMDD**, **YYYY-MM-DD**, or **DD/MM/YY**.")

	def parse_time(self, time:str, throw:bool = True) -> str | None:
		if time is None or time.lower() == "latest":
			return "\d{6}"

		if re.match(r"^[0-2][0-9][\.:]?[0-5][0-9][\.:]?[0-5][0-9]", time):
			return re.sub(r'[\.:]', '', time)
		if re.match(r"^[0-2][0-9][\.:]?[0-5][0-9]", time):
			return re.sub(r'[\.:]', '', time) + r'\d{2}'
		if not re.match(r"[0-2][0-9][0-5][0-9]", time):
			if throw:
				raise ValueError("Invalid time format. Try **HHMM**.")

	def parse_graph_input(self, input:str = None) -> tuple:
		# check if input is empty
		if input is None:
			input = "latest"
		# split input per space
		inputs = input.split(" ")
		# check if input is a date
		date:str = None
		time:str = None
		session:str = "(R|Q|FP)"
		top:list[int] = None
		number:int|None = None
		for input in inputs:
			if input.lower() == "latest":
				date = "\d{6}"
				time = "\d{6}"
				session = '(R|Q|FP)'
			else:
				# check if input is a date
				date = self.parse_date(input, False)
				# check if input is a time
				time = self.parse_time(input, False)
				if date is None:
					date = "\d{6}"
				if time is None:
					time = "\d{6}"
			# check if input has a race type: R, Q, FP
			if input.lower() in ["r", "q", "fp"]:
				session = input.upper()
			if input.startswith("#"):
				number = int(input.replace("#", ""))
			if re.match(r"^[0-9]+-[0-9]+$", input):
				top = input.split("-")
				# convert to int
				top = [int(top[0]), int(top[1])]
				if int(top[0]) > int(top[1]):
					raise ValueError("Invalid range. The first number must be lower than the second.")
			# check if input is a car number
		if number is not None:
			top = None
		return date, time, session, top, number

	@commands.command(
		description = "Show a graph of drivers lap times",
		usage = "graph [input with date and time or latest and maybe type of the race and #car number or 1-10 for top 10]",
		hidden = False,
	)
	@commands.guild_only()
	@commands.is_owner()
	@commands.has_permissions(moderate_members=True)
	async def graph(self, ctx:commands.Context, *, input:str = None) -> None:
		"""
		Show a graph of drivers lap times
		```
		{ctx.prefix}graph 241231 235959 r
		{ctx.prefix}graph 241231 235959 q
		{ctx.prefix}graph 241231 235959 fp
		{ctx.prefix}graph latest
		{ctx.prefix}graph latest r 1-10
		{ctx.prefix}graph latest r #21
		{ctx.prefix}graph 241231 235959 q 5-10
		{ctx.prefix}graph 241231 235959 fp #21
		```
		"""
		try:
			print(f"graph")
			async with ctx.typing():
				# check if input is a date
				config = self.bot.get_config(ctx.guild, "race", "graph")
				date, time, session, top, number = self.parse_graph_input(input)
				print(f"\ndate: {date}\ntime: {time}\nsession: {session}\ntop: {top}\nnumber: {number}\n")
				# get the results from temp result directory
				temp = self.bot.get_temp("results")
				regexp = f"^{date}_{time}_{session}\.result\.json$"
				resultFile = Dest.scan(temp, regexp, 'last')
				if resultFile is None:
					raise ValueError("No results found. Run the race, qualify or practice command first.")
				# get date and time and session from filename: 240309_220433_R.json.result.json
				filename = Dest.filename(resultFile)
				print(f"filename: {filename}")
				date, time, session = filename.split(".")[0].split("_")
				print(f"date: {date}\ntime: {time}\nsession: {session}")
				_top = f"{top[0]}-{top[1]}" if top is not None else "all"
				_number = f"{number}" if number is not None else "all"
				jsonFile = f"{date}_{time}_{session}_{_top}_{_number}.json"
				print(f"jsonFile: {jsonFile}")
				pngFile = f"{date}_{time}_{session}_{_top}_{_number}.png"
				print(f"pngFile: {pngFile}")
				# check if png file exists

				if Dest.exists(Dest.join(temp, pngFile)):
					await ctx.send(
						file=discord.File(
							Dest.join(temp, pngFile)
						)
					)
					return

				# load the result sa json
				result = Dest.json.load(resultFile)
				if len(result['laps']) == 0:
					raise ValueError(f"No laps found, no data to graph. Maybe apply a race type as I found an empty {result['typeName']} session.")
				#print(f"data: {data}")
				data = []
				fastest_laptime_ms = 999999999
				slowest_laptime_ms = 0
				#max_laps = 0
				slowest_laptimes = {}
				fastest_laptimes = {}
				position = 1
				for car in result['cars'].values():
					for driver in car['drivers'].values():
						if number is not None and car['number'] != number:
							continue
						if top is not None and position > top[1]:
							continue
						if top is not None and position < top[0]:
							continue
						lap = 0
						for laptime_ms in driver['laps']:
							if lap == 0:
								lap += 1
								continue
							laptime = self.convert_time(laptime_ms)
							if slowest_laptime_ms < laptime_ms:
								slowest_laptime_ms = laptime_ms
							if fastest_laptime_ms > laptime_ms:
								fastest_laptime_ms = laptime_ms
							data.append({
								"driver": f"#{car['number']} {driver['lastName']}",
								"lap": lap,
								"laps": len(driver['laps']) - 1, # -1 for formation lap
								"laptime": laptime,
								"laptime_ms": laptime_ms,
							})
							if laptime_ms > slowest_laptimes.get(driver['playerId'], 0):
								slowest_laptimes[driver['playerId']] = laptime_ms
							if laptime_ms < fastest_laptimes.get(driver['playerId'], 999999999):
								fastest_laptimes[driver['playerId']] = laptime_ms
							lap += 1
					position += 1
				# save the figure as json
				if len(data) == 0:
					raise ValueError("No data found.")
				Dest.json.save(
					Dest.join(temp, jsonFile),
					data,
				)
				df = pd.DataFrame(data)
				# create a figure and axis
				fig = px.line(
					df,
					x = "lap",
					y = "laptime_ms",
					line_shape = "spline",
					color = "driver",
					title = f"{result['server']} · {self.fullTrackName(result['track'])} · {result['typeName']} · {result['session']['laps']} laps",
					labels = {
						"laptime_ms": "Lap Time (ms)",
						"lap": "Laps",
						"driver": "Drivers",
					},
					markers = True,
					template = config['template'],
					range_x = [1, result['session']['laps']],
				)
				width = max(config['lap_spacing'] * result['session']['laps'] + 400, config['min_width'])
				height = config['min_height']
				fig.update_layout(
					xaxis = dict(
						tickmode = 'linear',
					),
					width = width,
					height = height,
				)
				fig.update_yaxes(
					tickvals = df['laptime_ms'],
					ticktext = df['laptime'],
					#range = [fastest_laptime_ms, slowest_average_laptime_ms],
					title = "Laptime"
				)
				fig.update_traces(
					line = {
						'width': 5,
					}
				)
				"""
				if config['logo']['source']:
					fig.add_layout_image(
						dict(
							source = config['logo']['source'],
							xref = "paper",
							yref = "paper",
							x = 1,
							y = 1,
							sizex = 0.2,
							sizey = 0.2,
							xanchor = "right",
							yanchor = "bottom",
						)
					)
				"""
				# save the figure as png
				fig.write_image(
					Dest.join(temp, pngFile)
				)
				# send the png
				await ctx.send(
					file=discord.File(
						Dest.join(temp, pngFile)
					)
				)
		except ValueError as e:
			traceback.print_exc()
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

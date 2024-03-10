"""
Login to ACC Dedicated Server via FTP and get the race results.
"""
import os
#import sys
import json
import ftplib
from datetime import datetime, timedelta, timezone
import re
#import discord
#from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands
from discord import app_commands
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
			storage = self.bot.get_temp("results")
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
				local_filename = os.path.join(storage, filename)
				result.append(local_filename)
				if not os.path.exists(local_filename):
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
			with open(filename, "rb") as f:
				data = json.load(f)
			drivers = []
			cars = {}
			positions = []
			fastest = {}
			laps = 0
			time = 0
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
							"lap": position["timing"]["lapCount"],
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
						"laps": position["timing"]["lapCount"],
						"time": position["timing"]["totalTime"],
					})
					# update car total time
					if time == 0:
						time = position["timing"]["totalTime"]
					# update car total laps
					if laps == 0:
						laps = position["timing"]["lapCount"]
			if len(data["laps"]):
				lap = 1
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
									fastest["lap"] = carLaps[carId]
									driver["best"]["fastest"] = True
							for i, s in enumerate(l["splits"]):
								if driver["best"]["splits"][i] == 0:
									driver["best"]["splits"][i] = s
								elif s < driver["best"]["splits"][i]:
									driver["best"]["splits"][i] = s
							driver["time"] += l["laptime"]
					lap += 1
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
				"laps": laps,
				"time": time,
				"cars": cars,
				"drivers": drivers,
				"positions": positions,
				"fastest": fastest,
			}
		except Exception as e:
			self.bot.debug(e)
			raise e


	async def handle_result(self, ctx:commands.Context, file:str, date:datetime) -> None:
		try:
			print(f"handle_result: {file}")
			data = self.load_result(file)
			# example data = tmp/output.json
			# save the result to a file with tab separated values
			with open(f"{file}.result.json", "w") as f:
				json.dump(data, f, indent='\t')
			if data is None:
				raise ValueError("Error loading result.")
			track = self.fullTrackName(data["track"])
			if data["laps"] == 0:
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
				description = f"**{track}** · **{data['laps']} laps** in **{self.convert_time(data['time'])}** {'🌧️' if data['wet'] == 1 else ''}",
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
			config = self.bot.get_config(ctx.guild, "connect", "acc")
			latest = False
			if config is None:
				raise ValueError("ACC Dedicated Server configuration not found.")
			if session not in ["FP", "Q", "R"]:
				raise ValueError("Session must be one of **FP**, **Q**, **R**.")
			if date is None or date == "" or date.lower() == "latest":
				print("latest")
				date = "\d{6}"
				date_str = "latest"
				time = "\d{6}"
				time_str = "latest"
				latest = True
			else:
				print("not latest")
				if date.lower() == "today":
					date = datetime.now(timezone.utc)
				elif date.lower() == "yesterday":
					date = datetime.now(timezone.utc) - timedelta(days=1)
				elif re.match(r"^[0-9]{2}[0-1][0-9][0-3][0-9]$", date):
					date = datetime.strptime(date, "%y%m%d")
				elif re.match(r"^[1-2][0-9][0-9]{2}[0-1][0-9][0-3][0-9]$", date):
					date = datetime.strptime(date, "%Y%m%d")
				elif re.match(r"^[0-9]{4}-[0-1]?[0-9]-[0-3]?[0-9]$", date):
					date = datetime.strptime(date, "%Y-%m-%d")
				elif re.match(r"^[0-3]?[0-9]/[0-1]?[0-9]/[0-9]{2}$", date):
					date = datetime.strptime(date, "%d/%m/%y")
				elif re.match(r"^[0-3]?[0-9]/[0-1]?[0-9]/[0-9]{4}$", date):
					date = datetime.strptime(date, "%d/%m/%Y")
				else:
					raise ValueError("Invalid date format. Try **YYMMDD**, **YYYYMMDD**, **YYYY-MM-DD**, or **DD/MM/YY**.")
				date_str = date.strftime("%d %B %Y")
				if time is None:
					time = r"\d{6}"
					time_str = "any time"
				else:
					if time == "latest":
						time = r"\d{6}"
						time_str = "latest"
						latest = True
					else:
						if re.match(r"[0-2][0-9][\.:]?[0-5][0-9][\.:]?[0-5][0-9]", time):
							time = re.sub(r"[\.:]", "", time)
						if not re.match(r"[0-2][0-9][0-5][0-9][0-5][0-9]", time):
							raise ValueError("Invalid time format. Try **HHMMSS**.")
						time_str = time
			if date_str == "latest":
				pattern = f"{date}_{time}_{session}.json"
			else:
				pattern = f"{date.strftime('%y%m%d')}_{time}_{session}.json"
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
					_, time, _ = os.path.basename(result).split("_")
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
			date, time, _ = os.path.basename(results[0]).split("_")
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
				local_filename = os.path.join(storage, filename)
				if not os.path.exists(local_filename):
					with open(local_filename, "wb") as file:
						self.ftp.retrbinary(f"RETR {filename}",
							file.write
						)
				# open the file as json
				with open(local_filename, "rb") as f:
					data = json.load(f)
				# check if the file is empty
				if len(data["sessionResult"]["leaderBoardLines"]) == 0:

					r = self.ftp.delete(filename)
					print(f"delete: {filename} {r}")
					#exit()
					# rename local file to .backup.json

					os.rename(local_filename, f"{local_filename}.backup.json")
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

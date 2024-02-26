"""

Login to GPortal via FTP and get the race results.

"""

import os, sys
import json
import ftplib
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import re

import discord
from discord.ext import commands

class GPortal(commands.Cog, name="GPortal"):
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

	def get_results(self, config, pattern:str) -> list | None:
		try:
			if (config['host'] is None or
				config['port'] is None or
				config['username'] is None or
				config['password'] is None or
				config['directory'] is None or
				config['storage'] is None):
				return None
			self.ftp.connect(config['host'], config['port'])
			self.ftp.login(config['username'], config['password'])
			self.ftp.cwd(config['directory'])
			storage = config['storage']
			# check if storage directory exists and create if not
			if not os.path.exists(storage):
				os.makedirs(storage)
			files = []
			self.ftp.retrlines("LIST", files.append)
			filenames = [line.split()[-1] for line in files]
			filenames.reverse()
			result = []
			for filename in filenames:
				if not re.match(pattern, filename):
					continue
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
			self.bot.warn(e)

	def parse_result(self, filename:str) -> dict:
		try:
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
				for c in data["sessionResult"]["leaderBoardLines"]:
					carId = c["car"]["carId"]
					car = {
						"number": c["car"]["raceNumber"],
						"car": c["car"]["carModel"],
						"cup": c["car"]["cupCategory"],
						"group": c["car"]["carGroup"],
						"team": c["car"]["teamName"],
						"laps": 0,
						"time": 0,
						"drivers": {},
					}
					if len(c["car"]["drivers"]) > 0:
						idx = 0
						for d in c["car"]["drivers"]:
							car["drivers"][idx] = {
								"firstName": d["firstName"],
								"lastName": d["lastName"],
								"shortName": d["shortName"],
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
						"laps": c["timing"]["lapCount"],
						"time": c["timing"]["totalTime"],
					})
			if len(data["laps"]):
				lap = 1
				for l in data["laps"]:
					carId = l["carId"]
					driverIdx = l["driverIndex"]
					if carId in cars:
						car = cars[carId]
						car["laps"] += 1
						car["time"] += l["laptime"]
						if driverIdx in car["drivers"]:
							driver = car["drivers"][driverIdx]
							#driver["laps"] += 1
							driver["laps"].append(l["laptime"])
							if l["isValidForBest"]:
								driver["best"]["lap"] = lap
								driver["best"]["time"] = l["laptime"]
								if fastest["time"] == l["laptime"]:
									fastest["car"] = carId
									fastest["driver"] = driverIdx
									fastest["lap"] = lap
									driver["best"]["fastest"] = True
							for i, s in enumerate(l["splits"]):
								if driver["best"]["splits"][i] == 0:
									driver["best"]["splits"][i] = s
								elif s < driver["best"]["splits"][i]:
									driver["best"]["splits"][i] = s
							driver["time"] += l["laptime"]
							# update car total time
							if time < l["laptime"]:
								time = car["time"]
							# update car total laps
							if laps < car["laps"]:
								laps = car["laps"]

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
								"violation": p["violationInLap"],
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
								"violation": p["violationInLap"],
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
			self.bot.warn(e)

	def parse_race_result(self, filename:str) -> dict | None:
		try:
			date = os.path.basename(filename).split("_")[0]
			with open(filename, "rb") as f:
				data = json.load(f)
			trackName = data["trackName"]
			fastestLapTime = data["sessionResult"]["bestlap"]
			positions = []
			place = 1
			fastestLapCar = None
			if len(data["sessionResult"]["leaderBoardLines"]) > 0:
				for line in data["sessionResult"]["leaderBoardLines"]:
					if fastestLapTime == line["timing"]["bestLap"]:
						fastestLapCar = line["car"]
					positions.append(
						{
							"place": place,
							"carId": line["car"]["carId"],
							"number": line["car"]["raceNumber"],
							"driver": line["currentDriver"]["lastName"],
							#"bestLap": line["timing"]["bestLap"],
							#"totalTime": line["timing"]["totalTime"],
							#"lapCount": line["timing"]["lapCount"],
							"bestLap": str(datetime.fromtimestamp(line["timing"]["bestLap"] / 1000).strftime("%M:%S.%f")[:-3]),
							"totalTime": str(datetime.fromtimestamp(line["timing"]["totalTime"] / 1000).strftime("%M:%S.%f")[:-3]),
						}
					)
					place += 1
			fastestLap = None
			fastestLapCarDriver = 0
			# every lap with lap index
			carLap = {}
			if len(data['laps']) > 0:
				l = 1
				for lap in data["laps"]:
					if lap["carId"] not in carLap:
						carLap[lap["carId"]] = 0
					carLap[lap["carId"]] += 1
					if fastestLapTime == lap["laptime"]:
						fastestLap = carLap[lap["carId"]]
						fastestLapCarDriver = lap["driverIndex"]
						fastestLapTime = str(datetime.fromtimestamp(fastestLapTime / 1000).strftime('%M:%S.%f')[:-3])
						break
					l += 1
			humanDate = datetime.strptime(date, '%y%m%d').strftime('%d %B %Y')
			return {
				"track": trackName,
				"date": humanDate,
				"positions": positions,
				"fastest":
				{
					"time": fastestLapTime,
					"lap": fastestLap,
					"car": fastestLapCar,
					"driver": fastestLapCarDriver,
				}
			}
		except Exception as e:
			self.bot.warn(e)

	async def handle_results(self, ctx:commands.Context, type:str, date:str, time:str) -> None:
		try:
			race_type = {
				"FP": "Free Practice",
				"Q": "Qualifying",
				"R": "Race",
			}.get(type)
			if race_type is None:
				raise ValueError("Invalid race type")

			pattern = f'^{date}_{time}_{type}\.json$'
			config = self.bot.get_config(ctx.guild, "connect", "gportal")
			if config is None:
				raise ValueError("GPortal configuration not found")
			results = self.get_results(config, pattern)
			if results is None:
				raise ValueError("No results found")
			#print(results)
			if type == "R":
				# if results are empty, report no results found
				if len(results) == 0:
					print("No results found")
					return await ctx.send(
						"No results found"
					)
				# if results are more than 1, report multiple results found and list all of them
				if len(results) > 1:
					print("Multiple results found")
					times = []
					for result in results:
						# split the date and time from the filename (240207_221110_R.json)
						_, time, _ = os.path.basename(result).split("_")
						times.append(
							time
						)
					times = "\n".join(times)
					embed = self.bot.embed(
						title = f"Multiple results found for on this date: {date}",
						description = "Please specify the time:\n\n"\
							f"```{times}```",
						bot = True,
					)
					return await ctx.send(
						embed = embed
					)
				result = self.parse_result(results[0])
				#print(f"Result: {result}")
				if len(result['positions']) == 0:
					embed = self.bot.embed(
						title = f"{race_type} results on {self.fullTrackName(result['track'])}, {result['date']}",
						description = "No results found",
						bot = True,
					)
					embed.set_footer(
						text = "Powered by Bang Systems"
					)
					return await ctx.send(
						embed = embed
					)
				embed = self.bot.embed(
					title = f"{race_type} results on {self.fullTrackName(result['track'])}, {result['date']}",
					description = "And the winner is...",
					bot = True,
				)
				for position in result['positions']:
					embed.add_field(
						name = f"{self.place(position['place'])}",
						value = f"#{position['number']} {position['driver']}"
					)
				# pretty print the fastest lap
				if len(result['fastest']) > 0:
					embed.add_field(
						name = "Fastest Lap",
						value = f"#{result['fastest']['car']['raceNumber']}"\
								f" {result['fastest']['car']['drivers'][result['fastest']['driver']]['lastName']}"\
								f" - {result['fastest']['time']} on lap {result['fastest']['lap']}.",
						inline = False
					)
			else:
				# type is free practice or qualifying
				# show the fastest lap for each car and how many laps they did

			embed.set_footer(
				text = "Powered by Bang Systems"
			)
			return await ctx.send(
				embed = embed
			)
		except Exception as e:
			await self.bot.error(e, guild=ctx.guild)

	@commands.command(
		description="Get the results of the date",
		hidden=False,
		aliases=[
			"result",
			"race_results",
		]
	)
	@commands.guild_only()
	async def race(self, ctx:commands.Context, date:str = None, time:str = None) -> None:
		try:
			# check if date is None
			if date is None:
				date = datetime.now().strftime('%y%m%d')
			# check if date is in the correct format YYMMDD
			if len(date) != 6:
				raise ValueError("Date must be in the format YYMMDD")
			if not date.isdigit():
				raise ValueError("Date must be in the format YYMMDD")
			date = datetime.strptime(date, '%y%m%d')
			date = date.strftime('%y%m%d')
			# check if time is None
			if time is None:
				time = "[0-9]{6}"
			# check if time is in the correct format HHMMSS
			else:
				if not re.match(r'^[0-2][0-9][0-5][0-9][0-5][0-9]$', time):
					raise ValueError("Time must be in the format HHMMSS")
			await self.handle_results(
				ctx,
				"R",
				date,
				time
			)
		except ValueError as e:
			await ctx.send(
				f"Error: {e}"
			)
		except Exception as e:
			await self.bot.error(e, guild=ctx.guild)


	@commands.command(
		description="Get the results of the date",
		hidden=False,
		aliases=[
			"qualifying",
			"qualifying_results",
		]
	)
	@commands.guild_only()
	async def qualify(self, ctx:commands.Context, date:str = None, time:str = None) -> None:
		try:
			# check if date is None
			if date is None:
				date = datetime.now().strftime('%y%m%d')
			# check if date is in the correct format YYMMDD
			if len(date) != 6:
				raise ValueError("Date must be in the format YYMMDD")
			if not date.isdigit():
				raise ValueError("Date must be in the format YYMMDD")
			date = datetime.strptime(date, '%y%m%d')
			date = date.strftime('%y%m%d')
			# check if time is None
			if time is None:
				time = "[0-9]{6}"
			# check if time is in the correct format HHMMSS
			else:
				if not re.match(r'^[0-2][0-9][0-5][0-9][0-5][0-9]$', time):
					raise ValueError("Time must be in the format HHMMSS")
			await self.handle_results(
				ctx,
				"Q",
				date,
				time
			)
		except ValueError as e:
			await ctx.send(
				f"Error: {e}"
			)
		except Exception as e:
			await self.bot.error(e, guild=ctx.guild)

	@commands.command(
		description="Get the results of the date",
		hidden=False,
		aliases=[
			"free_practice",
			"practice_results",
		]
	)
	@commands.guild_only()
	async def practice(self, ctx:commands.Context, date:str = None, time:str = None) -> None:
		try:
			# check if date is None
			if date is None:
				date = datetime.now().strftime('%y%m%d')
			# check if date is in the correct format YYMMDD
			if len(date) != 6:
				raise ValueError("Date must be in the format YYMMDD")
			if not date.isdigit():
				raise ValueError("Date must be in the format YYMMDD")
			date = datetime.strptime(date, '%y%m%d')
			date = date.strftime('%y%m%d')
			# check if time is None
			if time is None:
				time = "[0-9]{6}"
			# check if time is in the correct format HHMMSS
			else:
				if not re.match(r'^[0-2][0-9][0-5][0-9][0-5][0-9]$', time):
					raise ValueError("Time must be in the format HHMMSS")
			await self.handle_results(
				ctx,
				"FP",
				date,
				time
			)
		except ValueError as e:
			await ctx.send(
				f"Error: {e}"
			)
		except Exception as e:
			await self.bot.error(e, guild=ctx.guild)

async def setup(bot:commands.Bot) -> None:
	try:
		await bot.add_cog(
			GPortal(
				bot
			)
		)
	except Exception as e:
		raise e



"""
The race result example data:
{
	"sessionType": "R",
	"trackName": "spa",
	"sessionIndex": 2,
	"raceWeekendIndex": 0,
	"metaData": "spa",
	"serverName": "Danish eMotorsport Series",
	"sessionType": "R",
	"sessionResult": {
		"bestlap": 140822,
		"bestSplits": [
			41545,
			61880,
			37352
		],
		"isWetSession": 0,
		"type": 1,
		"leaderBoardLines": [
			{
				"car": {
					"carId": 1002,
					"raceNumber": 21,
					"carModel": 35,
					"cupCategory": 2,
					"carGroup": "GT3",
					"teamName": "",
					"nationality": 0,
					"carGuid": -1,
					"teamGuid": -1,
					"drivers": [
						{
							"firstName": "",
							"lastName": "DxBang",
							"shortName": "PLY",
							"playerId": "M2533274792484058"
						}
					]
				},
				"currentDriver": {
					"firstName": "",
					"lastName": "DxBang",
					"shortName": "PLY",
					"playerId": "M2533274792484058"
				},
				"currentDriverIndex": 0,
				"timing": {
					"lastLap": 147430,
					"lastSplits": [
						42717,
						65647,
						39065
					],
					"bestLap": 145045,
					"bestSplits": [
						42037,
						63665,
						38347
					],
					"totalTime": 3704312,
					"lapCount": 20,
					"lastSplitId": 2
				},
				"missingMandatoryPitstop": 0,
				"driverTotalTimes": [
					1632095.5
				],
				"bIsSpectator": false
			},
			{
				"car": {
					"carId": 1001,
					"raceNumber": 14,
					"carModel": 35,
					"cupCategory": 0,
					"carGroup": "GT3",
					"teamName": "",
					"nationality": 0,
					"carGuid": -1,
					"teamGuid": -1,
					"drivers": [
						{
							"firstName": "",
							"lastName": "DenneBurn",
							"shortName": "DEN",
							"playerId": "M2533274866799377"
						}
					]
				},
				"currentDriver": {
					"firstName": "",
					"lastName": "DenneBurn",
					"shortName": "DEN",
					"playerId": "M2533274866799377"
				},
				"currentDriverIndex": 0,
				"timing": {
					"lastLap": 142550,
					"lastSplits": [
						41825,
						63072,
						37652
					],
					"bestLap": 140822,
					"bestSplits": [
						41545,
						61880,
						37352
					],
					"totalTime": 3717336,
					"lapCount": 20,
					"lastSplitId": 2
				},
				"missingMandatoryPitstop": 0,
				"driverTotalTimes": [
					1686321.0
				],
				"bIsSpectator": false
			}
		]
	},
	"laps": [
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 174460,
			"isValidForBest": true,
			"splits": [
				71625,
				63787,
				39047
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 157845,
			"isValidForBest": false,
			"splits": [
				41632,
				78212,
				38000
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 141860,
			"isValidForBest": true,
			"splits": [
				41545,
				62855,
				37460
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 141500,
			"isValidForBest": true,
			"splits": [
				41725,
				62422,
				37352
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 576461,
			"isValidForBest": false,
			"splits": [
				468183,
				66107,
				42170
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 176595,
			"isValidForBest": false,
			"splits": [
				41922,
				80742,
				53930
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 151750,
			"isValidForBest": false,
			"splits": [
				44027,
				66410,
				41312
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 149482,
			"isValidForBest": true,
			"splits": [
				45070,
				64765,
				39647
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 147587,
			"isValidForBest": true,
			"splits": [
				44147,
				64192,
				39247
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 506235,
			"isValidForBest": false,
			"splits": [
				402080,
				64710,
				39445
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 150080,
			"isValidForBest": false,
			"splits": [
				43702,
				66475,
				39902
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 143825,
			"isValidForBest": false,
			"splits": [
				42532,
				62700,
				38592
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 144977,
			"isValidForBest": false,
			"splits": [
				42172,
				64692,
				38112
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 142010,
			"isValidForBest": true,
			"splits": [
				41775,
				62777,
				37457
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 148100,
			"isValidForBest": false,
			"splits": [
				43912,
				65325,
				38862
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 140822,
			"isValidForBest": true,
			"splits": [
				41572,
				61880,
				37370
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 145045,
			"isValidForBest": true,
			"splits": [
				42037,
				64150,
				38857
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 147367,
			"isValidForBest": false,
			"splits": [
				41815,
				67842,
				37710
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 148435,
			"isValidForBest": false,
			"splits": [
				43685,
				63885,
				40865
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 179407,
			"isValidForBest": false,
			"splits": [
				43672,
				71257,
				64477
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 150905,
			"isValidForBest": false,
			"splits": [
				43955,
				67315,
				39635
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 155260,
			"isValidForBest": false,
			"splits": [
				42157,
				65050,
				48052
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 234192,
			"isValidForBest": false,
			"splits": [
				132100,
				64247,
				37845
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 418337,
			"isValidForBest": false,
			"splits": [
				316245,
				63875,
				38217
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 143937,
			"isValidForBest": false,
			"splits": [
				41685,
				63965,
				38287
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 144627,
			"isValidForBest": false,
			"splits": [
				41992,
				64135,
				38500
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 144885,
			"isValidForBest": false,
			"splits": [
				42092,
				63840,
				38952
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 150560,
			"isValidForBest": false,
			"splits": [
				41735,
				63140,
				45685
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 147835,
			"isValidForBest": false,
			"splits": [
				43392,
				65287,
				39155
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 142857,
			"isValidForBest": false,
			"splits": [
				41662,
				62377,
				38817
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 150452,
			"isValidForBest": false,
			"splits": [
				48750,
				63402,
				38300
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 161695,
			"isValidForBest": false,
			"splits": [
				59680,
				63742,
				38272
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 147235,
			"isValidForBest": false,
			"splits": [
				42857,
				65767,
				38610
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 144795,
			"isValidForBest": false,
			"splits": [
				41580,
				62867,
				40347
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 145257,
			"isValidForBest": true,
			"splits": [
				43245,
				63665,
				38347
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 143065,
			"isValidForBest": true,
			"splits": [
				41742,
				63517,
				37805
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 144815,
			"isValidForBest": false,
			"splits": [
				42805,
				63637,
				38372
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 143100,
			"isValidForBest": false,
			"splits": [
				41890,
				63437,
				37772
			]
		},
		{
			"carId": 1002,
			"driverIndex": 0,
			"laptime": 147430,
			"isValidForBest": true,
			"splits": [
				42717,
				65647,
				39065
			]
		},
		{
			"carId": 1001,
			"driverIndex": 0,
			"laptime": 142550,
			"isValidForBest": false,
			"splits": [
				41825,
				63072,
				37652
			]
		}
	],
	"penalties": [],
	"post_race_penalties": []
}
"""


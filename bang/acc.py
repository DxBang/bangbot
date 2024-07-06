from datetime import datetime, timezone, timedelta
import re
import pytz
from .dest import Dest
from .human import Human

class ACC:
	@staticmethod
	def parseDateRegexp(date:str = None, throw:bool = True) -> str | None:
		print(f"parseDate: {date} ({type(date)})")
		if date is None or date.lower() == "latest":
			return "\d{6}"
		return ACC.parseDate(date, throw)

	@staticmethod
	def parseDate(date:str = None, throw:bool = True) -> str | None:
		try:
			return Human.date(date)
		except Exception as e:
			if throw:
				raise e
			return None

	@staticmethod
	def parseTimeRegexp(time:str = None, throw:bool = True) -> str | None:
		print(f"parseTime: {time} ({type(time)}")
		if time is None or time.lower() == "latest" or time == "*":
			return "\d{6}"
		if re.match(r"^[0-2][0-9][\.:]?[0-5][0-9][\.:]?[0-5][0-9]", time):
			return re.sub(r'[\.:]', '', time)
		if re.match(r"^[0-2][0-9][\.:]?[0-5][0-9]", time):
			return re.sub(r'[\.:]', '', time) + r'\d{2}'
		if re.match(r"^[0-2][0-9]", time):
			return re.sub(r'[\.:]', '', time) + r'\d{4}'
		return ACC.parseTime(time, throw)

	@staticmethod
	def parseTime(time:str = None, throw:bool = True) -> str | None:
		try:
			return Human.time(time)
		except Exception as e:
			if throw:
				raise e
			return None

	@staticmethod
	def convertTime(ms:int) -> str:
		if ms >= 31536000000:
			return str(datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Yy %mn %dd %H:%M:%S.%f")[:-3])
		if ms >= 86400000:
			return str(datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%dd %H:%M:%S.%f")[:-3])
		if ms >= 3600000:
			return str(datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%H.%M:%S.%f")[:-3])
		if ms >= 60000:
			return str(datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%M:%S.%f")[:-3])
		return str(datetime.fromtimestamp(ms / 1000).strftime("%S.%f")[:-3])

	@staticmethod
	def fullTrackName(short:str) -> str:
		return {
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
			"red_bull_ring": "Red Bull Ring",
			"nurburgring_24h": "Nürburgring Nordshleife",
		}.get(short, short)

	@staticmethod
	def placePodium(place:int) -> str:
		return {
			1: "🥇",
			2: "🥈",
			3: "🥉",
		}.get(place, f"{place}.")

	@staticmethod
	def place(place:int, podium:bool = False) -> str:
		if podium and place in [1, 2, 3]:
			return ACC.placePodium(place)
		return {
			1: "1️⃣",
			2: "2️⃣",
			3: "3️⃣",
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

	@staticmethod
	def car(car:int) -> list | None:
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

			80: ["Audi R8 LMS GT2", 2021, "GT2"],
			82: ["KTM XBOW GT2", 2021, "GT2"],
			83: ["Maserati MC20 GT2", 2023, "GT2"],
			84: ["Mercedes AMG GT2", 2023, "GT2"],
			85: ["Porsche 911 GT2 RS CS Evo", 2023, "GT2"],
			86: ["Porsche 935", 2019, "GT2"],
		}.get(car, [f"Unknown Car #{car}", 0, "Unknown"])

	@staticmethod
	def driverName(driver:dict) -> str:
		if driver["name"] != "" and driver["surname"] != "":
			return f"{driver['name']} {driver['surname']}"
		elif driver["surname"] != "":
			return f"{driver['surname']}"
		elif driver["name"] != "":
			return f"{driver['name']}"
		elif driver["abbreviation"] != "":
			return f"{driver['abbreviation']}"
		return "Unknown"

	@staticmethod
	def carTeam(car:dict) -> str:
		# if car team is longer then 0, use team name
		if len(car.get("team", "")) > 0:
			return car.get("team")
		if len(car.get("drivers", [])) == 1:
			return ACC.driverName(car.get("drivers")[0])
		else:
			return "".join([
				ACC.driverName(driver)[:3]
				for driver in car.get("drivers", [])
			])

	@staticmethod
	def dateToEpoch(date:str, time:str = None, tz:str = None) -> int:
		date = Human.date(date) # datetime
		if time is not None:
			time = Human.time(time) # datetime
			date = datetime.combine(
				date,
				time.time()
			)
		if tz is None:
			return int(date.timestamp())
		tz = pytz.timezone(tz)
		combined = tz.localize(
			date
		)
		return int(combined.timestamp())

	@staticmethod
	def epochToDate(epoch:int, tz:str) -> str:
		return datetime.fromtimestamp(epoch, tz=timezone.tzname(tz)).strftime("%y%m%d %H%M%S")


	@staticmethod
	def sessionTimestampFiles(path:str) -> dict | None:
		files = Dest.scan(
			path,
			r"^\d{6}_\d{6}_(FP|Q|R)\.json$",
			"all"
		)
		ret:dict = {
			"r": {},
			"q": {},
			"fp": {},
		}
		for k, v in ret.items():
			print(f"r: {k} type: {type(v)}")
		"""
		ret = {
			"r": {
				"{timestamp}": "{file}",
				"{timestamp}": "{file}",
			},
			"q": {
				"{timestamp}": "{file}",
				"{timestamp}": "{file}",
			},
			"fp": {
				"{timestamp}": "{file}",
				"{timestamp}": "{file}",
			}
		}
		"""
		for file in files:
			#print(f"file: {file}")
			file = Dest.basename(file)
			date, time, session = Dest.filename(file).split("_")
			#print(f"date: {date}, time: {time}, session: {session}")
			timestamp = int(
					datetime.strptime(
					f"{date} {time}",
					"%y%m%d %H%M%S"
				).timestamp()
			)
			#print(f"timestamp: {timestamp}")
			#print(f"session: {session.lower()}")
			#print(f"ret type: {type(ret[session.lower()])}")
			ret[session.lower()].update({
				timestamp: file
			})
		return ret

	@staticmethod
	def sessionTimestampFilter(stamps:dict, target:int) -> dict | None:
		filtered = {k: v for k, v in stamps.items() if k <= target}
		if filtered:
			highest = max(filtered)
			return filtered[highest]
		return None

	@staticmethod
	def sessionRaceFile(path:str, date:str, time:str = None, stamps:dict = None) -> str | None:
		if stamps is None:
			stamps = ACC.sessionTimestampFiles(path).get("r")
		if stamps is None:
			return None
		print(f"stamps: {stamps}")
		date = Human.date(date).strftime("%y%m%d")
		time = Human.time(time).strftime("%H%M%S")
		timestamp = datetime.strptime(f"{date} {time}", "%y%m%d %H%M%S").timestamp()
		return ACC.sessionTimestampFilter(stamps, timestamp)

	@staticmethod
	def sessionQualifyingFile(path:str, date:str, time:str = None, stamps:dict = None) -> str | None:
		if stamps is None:
			stamps = ACC.sessionTimestampFiles(path).get("q")
		if stamps is None:
			return None
		date = Human.date(date).strftime("%y%m%d")
		time = Human.time(time).strftime("%H%M%S")
		timestamp = datetime.strptime(f"{date} {time}", "%y%m%d %H%M%S").timestamp()
		return ACC.sessionTimestampFilter(stamps, timestamp)

	@staticmethod
	def sessionFreePracticeFile(path:str, date:str, time:str = None, stamps:dict = None) -> str | None:
		if stamps is None:
			stamps = ACC.sessionTimestampFiles(path).get("fp")
		if stamps is None:
			return None
		date = Human.date(date).strftime("%y%m%d")
		time = Human.time(time).strftime("%H%M%S")
		timestamp = datetime.strptime(f"{date} {time}", "%y%m%d %H%M%S").timestamp()
		return ACC.sessionTimestampFilter(stamps, timestamp)

	@staticmethod
	def sessionFiles(path:str, date:str, time:str = None, free_practices:int = 1) -> dict | None:
		# create a regexp for based on the date to {date}_{time}_R.json
		ret = {
			"r": None,
			"q": None,
			"fp": None,
		}
		files = ACC.sessionTimestampFiles(path)
		date = Human.date(date).strftime("%y%m%d")
		time = Human.time(time).strftime("%H%M%S")
		timestamp = datetime.strptime(f"{date} {time}", "%y%m%d %H%M%S").timestamp()
		# find the race file
		file = ACC.sessionTimestampFilter(files.get("r"), timestamp)
		if file is None:
			return None
		ret["r"] = file
		# update the timestamp to this file
		date, time, _ = Dest.filename(file).split("_")
		timestamp = int(
			datetime.strptime(
				f"{date} {time}",
				"%y%m%d %H%M%S"
			).timestamp()
		) - 1
		# find the qualifying file
		file = ACC.sessionTimestampFilter(files.get("q"), timestamp)
		if file is not None:
			ret["q"] = file
			# update the timestamp to this file
			date, time, _ = Dest.filename(file).split("_")
			timestamp = int(
				datetime.strptime(
					f"{date} {time}",
					"%y%m%d %H%M%S"
				).timestamp()
			) - 1
			# check that it isn't related to another R file
			"""
			This needs to be implemented later... maybe, if it is needed.
			A race needs a qualifying session...
			"""
		if free_practices == 0:
			del ret["fp"]
			return ret
		if free_practices == 1:
			file = ACC.sessionTimestampFilter(files.get("fp"), timestamp)
			if file is not None:
				ret["fp"] = file
		else:
			# find the free practice files
			ret["fp"] = []
			for i in range(free_practices):
				file = ACC.sessionTimestampFilter(files.get("fp"), timestamp)
				if file is None:
					break
				# update the timestamp to this file
				date, time, _ = Dest.filename(file).split("_")
				timestamp = int(
					datetime.strptime(
						f"{date} {time}",
						"%y%m%d %H%M%S"
					).timestamp()
				) - 1
				ret["fp"].append(file)
		return ret

	@staticmethod
	def loadSession(file:str) -> dict | None:
		# tmp/sessions/test.json
		if Dest.exists(file):
			_session = Dest.json.load(file)
			session = {
				"r": None,
				"q": None,
				"fp": None,
			}
			for k, v in _session.items():
				if k in session:
					session[k] = v
			return session
		return None

	@staticmethod
	def loadSessionResult(file:str) -> dict | None:
		resultFile = Dest.suffix(file, ".result")
		if Dest.exists(resultFile):
			return ACC.load(resultFile)
		if Dest.exists(file):
			result = ACC.loadACCConverted(file)
			if result is not None:
				ACC.save(resultFile, result)
				return result
		return None

	@staticmethod
	def session(path:str, date:datetime, time:datetime = None, free_practices:int = 1) -> dict | None:
		files = ACC.sessionFiles(path, date, time, free_practices)
		if files is None:
			raise FileNotFoundError(f"No session files found in {path} for {date} {time} with {free_practices} free practices.")
		date, time, _ = Dest.filename(files.get("r")).split("_")
		ret = {
			"version": "0.1",
			"info": {
				"datetime": datetime.strptime(f"{date} {time}", "%y%m%d %H%M%S"),
				"files": files,
			},
			"r": None,
			"q": None,
			"fp": None,
		}
		for session, file in files.items():
			if file is None:
				continue
			if session == "fp":
				if free_practices == 1:
					ret[session] = ACC.loadSessionResult(Dest.join(path, file))
					continue
				else:
					ret[session] = []
					for _file in file:
						ret[session].append(ACC.loadSessionResult(Dest.join(path, _file)))
					continue
			ret[session] = ACC.loadSessionResult(Dest.join(path, file))
		return ret

	@staticmethod
	def load(file:str) -> dict:
		return Dest.json.load(
			file,
			True
		)
	@staticmethod
	def save(file:str, data:dict) -> None:
		Dest.json.save(
			file,
			data
		)

	@staticmethod
	def convertACC(data:dict) -> dict | None:
		try:
			if data.get("sessionType", None) is None:
				raise KeyError("Invalid result file. Missing 'sessionType' key.")
			if data.get("sessionResult", None) is None:
				raise KeyError("Invalid result file. Missing 'sessionResult' key.")
			bestLapDriver = None
			bestLapTime = data.get("sessionResult").get("bestlap", 0)
			leader:dict = data.get("sessionResult").get("leaderBoardLines")[0]
			session:dict = {
				"name": data.get("serverName", ""),
				"index": data.get("sessionIndex", 0),
				"weekend": data.get("weekendIndex", 0),
				"wet": data.get("sessionResult").get("isWetSession", 0),
				"laps": leader.get("timing").get("lapCount"),
				"time": leader.get("timing").get("totalTime"),
				"best": {
					"lap": None,
					"split": data.get("sessionResult").get("bestSplits", []),
				},
				"type": {
					"tag": data.get("sessionType", ""),
					"name": {
						"FP": "Free Practice",
						"Q": "Qualifying",
						"R": "Race",
					}.get(data.get("sessionType", ""), "Unknown"),
					"result": data.get("sessionResult").get("type", -1),
				},
				"track": {
					"tag": data.get("trackName", ""),
					"name": ACC.fullTrackName(data.get("trackName", "")),
				},
			}
			positions:dict = []
			cars:dict = {}
			penalties:dict = {
				"race": {},
				"post": {},
			}
			# temps
			carLaps:dict = {}
			carTime:dict = {}
			for _position in data.get("sessionResult", {}).get("leaderBoardLines"):
				_car = _position.get("car")
				_drivers = _car.get("drivers")
				carId = _car.get("carId")
				carLaps.setdefault(carId, 0)
				carTime.setdefault(carId, 0)
				drivers:list = []
				# for idx, _driver in enumerate(_drivers):
				for _driver in _drivers:
					driver:dict = {
						"playerId": _driver.get("playerId", ""),
						"name": _driver.get("firstName", ""),
						"surname": _driver.get("lastName", ""),
						"abbreviation": _driver.get("shortName", ""),
					}
					drivers.append(driver)
				carModel = ACC.car(_car.get("carModel", 0))
				car:dict = {
					"number": _car.get("raceNumber", 0),
					"cup": _car.get("cupCategory", 0),
					"team": _car.get("teamName", ""),
					"group": _car.get("carGroup", ""),
					"nationality": _car.get("nationality", ""),
					"model": dict(
						id = _car.get("carModel", 0),
						name = carModel[0],
						year = carModel[1],
						group = carModel[2],
					),
					"drivers": drivers,
				}
				cars.update({
					carId: car
				})
				# positions
				position = {
					"carId": carId,
					"driverId": _position.get("currentDriverIndex", 0),
					"timing": {
						"laps": _position.get("timing").get("lapCount"),
						"time": _position.get("timing").get("totalTime"),
						"best": {
							"lap": _position.get("timing").get("bestLap"),
							"split": _position.get("timing").get("bestSplits"),
						},
						"drivers": _position.get("driverTotalTimes"),
					},
					"pitstop": _position.get("missingMandatoryPitstop"),
				}
				if session.get("laps") < _position.get("timing").get("lapCount"):
					session["laps"] = _position.get("timing").get("lapCount")
				positions.append(position)
			laps:list = [[] for _ in range(session.get("laps"))]
			for _lap in data.get("laps", []):
				carId:int = _lap["carId"]
				# remove this if they have fixed the lap zero issue (lap zero bug in ACC)
				if carLaps.get(carId) == 0:
					_lap["laptime"] = 0 # reset lap zero, since ACC counts the lap way before race start
					_lap["splits"][0] = 0 # reset split zero, since ACC counts the lap way before race start
				# end remove
				driverIndex:int = _lap["driverIndex"]
				laptime:int = _lap["laptime"]
				lap = carLaps[carId]
				idx = lap # - 1 only if lap zero is removed
				carTime[carId] += laptime
				laps[idx].append({
					#"@position": 0, # redundant as it is sorted in current level
					#"@lap": lap, # redundant as it is sorted in previous level
					#"@driver": ACC.driverName(cars.get(carId).get("drivers")[driverIndex]),
					#"@time": ACC.convertTime(laptime),
					"carId": carId,
					"driverId": driverIndex,
					"valid": _lap.get("isValidForBest", False),
					"time": laptime,
					"total": carTime.get(carId),
					"split": _lap.get("splits", []),
				})
				if bestLapDriver is None and laptime == bestLapTime:
					bestLapDriver = {
						"time": laptime,
						"lap": lap,
						"carId": carId,
						"driverId": driverIndex,
					}
					session["best"]["lap"] = bestLapDriver
				carLaps[carId] += 1
			for idx, _cars in enumerate(laps):
				#laps[idx] = sorted(_cars, key=lambda x: x["total"])
				# fix position
				if '@position' in _cars[0]:
					for position, car in enumerate(laps[idx]):
						car["@position"] = position + 1
			# penalties
			_penalties = [
				{"field": "penalties", "type": "race"},
				{"field": "post_race_penalties", "type": "post"},
			]
			for penalty in _penalties:
				for _penalty in data.get(penalty.get("field"), []):
					if _penalty.get("penalty") == "None":
						continue
					carId = _penalty.get("carId")
					if carId not in penalties.get(penalty.get("type")):
						penalties.get(penalty.get("type")).update({
							carId: []
						})
					penalties.get(penalty.get("type")).get(carId).append(
						{
							"driver": _penalty.get("driverIndex", 0),
							"reason": _penalty.get("reason", ""),
							"penalty": _penalty.get("penalty", ""),
							"value": _penalty.get("penaltyValue", 0),
							"violated": _penalty.get("violationInLap", 0),
							"cleared": _penalty.get("clearedInLap", 0),
						}
					)
			return dict(
				version = "0.2",
				session = session,
				positions = positions,
				cars = cars,
				laps = laps,
				penalties = penalties,
			)
		except Exception as e:
			raise e

	@staticmethod
	def loadACC(file:str) -> dict:
		return Dest.json.load(
			file,
			True
		)

	@staticmethod
	def loadACCConverted(file:str) -> None:
		return ACC.convertACC(
			ACC.loadACC(file)
		)

	@staticmethod
	def parseRaceInput(input:str = None) -> tuple:
		date:datetime = None
		time:datetime = None
		session:str = 'R'
		top:list[int] = []
		numbers:list[int] = []
		sync:bool = False
		limit:int = 14
		server:str = None
		if input is None:
			return server, date, time, session, top, numbers, sync, limit
		inputs = input.split(" ")
		for input in inputs:
			if input.lower() in ["r", "q", "fp", "f", "p"]:
				if input.lower() in ["f", "p"]:
					session = "FP"
					continue
				session = input.upper()
				continue
			if re.match(r"^\d{1,2}-\d{1,2}?$", input):
				top = [int(number) for number in input.split("-")]
				continue
			if re.match(r"^\d$", input):
				top = [int(input), int(input)]
				continue
			if input.startswith("#"):
				numbers = [int(number) for number in input[1:].split(",")]
				continue
			if input.lower() in ["sync", "s", "y", "yes", "true", "t"]:
				sync = True
				continue
			if sync:
				if input.lower() in ["all", "full", "complete", "everything", "every", "e"]:
					limit = 0
					continue
			# get server name based on random letters and maybe numbers at the end
			if re.match(r"^[A-z]+([-\,\.0-9]+)?$", input):
				server = input
				continue
			if date is None:
				date = ACC.parseDate(input)
				continue
			if date is not None and time is None:
				time = ACC.parseTime(input)
				continue
		return server, date, time, session, top, numbers, sync, limit

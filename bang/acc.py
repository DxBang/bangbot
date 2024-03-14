from datetime import datetime, timezone, timedelta
import re

class ACC:
	@staticmethod
	def parse_date(date:str = None, throw:bool = True) -> str | None:
		print(f"parse_date: {date} ({type(date)})")
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

	@staticmethod
	def parse_time(time:str = None, throw:bool = True) -> str | None:
		print(f"parse_time: {time} ({type(time)}")
		if time is None or time.lower() == "latest":
			return "\d{6}"
		if re.match(r"^[0-2][0-9][\.:]?[0-5][0-9][\.:]?[0-5][0-9]", time):
			return re.sub(r'[\.:]', '', time)
		if re.match(r"^[0-2][0-9][\.:]?[0-5][0-9]", time):
			return re.sub(r'[\.:]', '', time) + r'\d{2}'
		if not re.match(r"[0-2][0-9][0-5][0-9]", time):
			if throw:
				raise ValueError("Invalid time format. Try **HHMM**.")

	@staticmethod
	def convert_time(ms:int) -> str:
		if ms >= 31536000000:
			return str(datetime.fromtimestamp(ms / 1000).strftime("%Yy %mn %dd %H:%M:%S.%f")[:-3])
		if ms >= 86400000:
			return str(datetime.fromtimestamp(ms / 1000).strftime("%dd %H:%M:%S.%f")[:-3])
		if ms >= 3600000:
			return str(datetime.fromtimestamp(ms / 1000).strftime("%H.%M:%S.%f")[:-3])
		if ms >= 60000:
			return str(datetime.fromtimestamp(ms / 1000).strftime("%M:%S.%f")[:-3])
		return str(datetime.fromtimestamp(ms / 1000).strftime("%S.%f")[:-3])

	@staticmethod
	def fullTrackName(short:str) -> str:
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

	@staticmethod
	def place(place:int) -> str:
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

	@staticmethod
	def car(car:int) -> dict:
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

	@staticmethod
	def driverName(driver:dict) -> str:
		if driver["firstName"] != "" and driver["lastName"] != "":
			return f"**{driver['firstName']} {driver['lastName']}**"
		elif driver["lastName"] != "":
			return f"**{driver['lastName']}**"
		else:
			return f"**{driver['shortName']}**"

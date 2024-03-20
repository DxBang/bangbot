import bang
import discord
from discord.ext import commands
import traceback
import re
import plotly.express as px
import pandas as pd
import base64
from bang.acc import ACC
from bang.dest import Dest
from bang.human import Human
from datetime import datetime


class Graph(commands.Cog, name="Graph"):
	__slots__ = (
		"bot",
		"ftp",
	)
	def __init__(self, bot:bang.Bot) -> None:
		try:
			self.bot = bot
		except Exception as e:
			raise e

	def fig_line_update_defaults(self, fig:px.line, config:dict, race:dict) -> px.line:
		try:
			width = max((config['lap_width'] * race['session']['laps']) + 400, config['min_width'])
			height = config['min_height']
			fig.update_layout(
				xaxis = dict(
					tickmode = "linear",
					title = dict(
						font = dict(
							size = config['label']['size'],
						)
					)
				),
				yaxis = dict(
					tickmode = "linear",
					title = dict(
						font = dict(
							size = config['label']['size'],
						)
					)
				),
				width = width,
				height = height,
				title = dict(
					font = dict(
						size = config['title']['size'],
					)
				),
				font = dict(
					size = config['font']['size'],
				),
				template = config['template'],
			)
			fig.update_traces(
				line = {
					'width': 5,
					'shape': 'spline',
				}
			)
			if config['logo']['source'] != "" and config['logo']['source'] is not None:
				logo = Dest.file(config['logo']['source'])
				if Dest.exists(logo):
					print(f"logo: {logo}")
					# get mime type
					mime = Dest.mime(logo)
					with open(logo, "rb") as f:
						logo = base64.b64encode(f.read()).decode()
					fig.add_layout_image(
						dict(
							source = f"data:{mime};base64,{logo}",
							xref = "paper",
							yref = "paper",
							x = config['logo']['x'],
							y = config['logo']['y'],
							sizex = config['logo']['sizex'],
							sizey = config['logo']['sizey'],
							xanchor = config['logo']['xanchor'],
							yanchor = config['logo']['yanchor'],
							opacity = config['logo']['opacity'],
							layer = "below",
						)
					)
			return fig
		except Exception as e:
			raise e


	def parse_graph_input(self, input:str = None) -> tuple[str, str, str, list[int], list[int]]:
		# check if input is empty
		return ACC.parseRaceInput(input)
		if input is None:
			input = "latest"
		# split input per space
		inputs = input.split(" ")
		# check if input is a date
		date:str = None
		time:str = None
		heat:str = "R"
		top:list[int] = []
		numbers:list[int] = []
		for input in inputs:
			print(f"input: {input}")
			if input.lower() in ["r", "q", "fp", "f"]:
				print(f"	heat: {input}")
				if input.lower() == "f":
					heat = "FP"
				else:
					heat = input.upper()
				continue
			if input.startswith("#"):
				print(f"	number: {input}")
				# remove # and split by comma
				numbers = [int(number) for number in input[1:].split(",")]
				continue
			if re.match(r"^[0-9]+-[0-9]+$", input):
				print(f"	top: {input}")
				top = input.split("-")
				# convert to int
				top = [int(top[0]), int(top[1])]
				if int(top[0]) > int(top[1]):
					raise ValueError("Invalid range. The first number must be lower than the second.")
				continue
			if date is None:
				try:
					date = Human.date(input)
					print(f"	date: {date}")
					if date is not None:
						continue
				except Exception as e:
					print(f"Date Error: {e}")
			if date is not None and time is None:
				try:
					time = Human.time(input)
					print(f"	time: {time}")
					if time is not None:
						continue
				except Exception as e:
					print(f"Time Error: {e}")
		if date is None:
			date = Human.date("latest")
			print(f"date: {date}")
		if time is None:
			time = Human.time("latest")
			print(f"time: {time}")
			# check if input is a car number
		return date, time, heat, top, numbers

	@commands.command(
		description = "Show a graph of drivers lap times",
		usage = "laptime [input with date and time or latest and maybe type of the race and #car number or 1-10 for top 10]",
		hidden = True,
		aliases = [
			"lap",
			"laptime",
		]
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def laptimes(self, ctx:commands.Context, *, input:str = None) -> None:
		try:
			print(f"laptimes")
			async with ctx.typing():
				date, time, heat, top, numbers = ACC.parseRaceInput(input)
				print(f"positions")
				print(f"\tdate: {type(date)} {date}")
				print(f"\ttime: {type(time)} {time}")
				print(f"\theat: {type(heat)} {heat}")
				print(f"\ttop: {type(top)} {top}")
				print(f"\tnumber: {type(numbers)} {numbers}")

				temp = self.bot.getTemp("results")
				session = ACC.session(
					temp,
					date,
					time,
					free_practices=0,
				)
				if session is None:
					raise ValueError("No results found for the given date (and time).")
				dt = session.get("info", {}).get("datetime", None)
				# get date and time and session from filename: 240309_220433_R.json.result.json
				file = f"{dt.strftime('%y%m%d')}_{dt.strftime('%H%M%S')}_{heat}.result.json"
				print(f"file: {file}")
				pngFile = Dest.extension(
					Dest.suffix(
						Dest.filename(file),
						".laptimes",
					), 'png'
				)
				print(f"pngFile: {pngFile}")
				# check if png file exists
				"""
				if Dest.exists(Dest.join(temp, pngFile)):
					return await ctx.send(
						file=discord.File(
							Dest.join(temp, pngFile)
						)
					)
				"""
				# prepare the graph
				label = self.bot.getConfig(ctx.guild, "label", "graph")
				config = self.bot.getConfig(ctx.guild, "graph")
				race = session.get("r")
				#quali = session.get("q")
				print("session info")
				Dest.json.print(session.get("info"))
				# check
				if len(race.get("laps", [])) == 0:
					# delete
					Dest.remove(file)
					raise ValueError(f"No laps found, no data to graph...")
				x:list[int] = []
				y:list[int] = []
				yTxt:list[str] = []
				car:list[str] = []
				cars = race.get("cars", {})
				slowest_laptime_ms = 0
				fastest_laptime_ms = 999999999
				carAvgLaptime:dict = {}
				showCars:list = []
				if top is not None and len(top) > 0:
					print(f"top {top}")
					for position, _car in enumerate(race["positions"]):
						if position <= top[1]-1 and position >= top[0]-1:
							print(f"	{_car['carId']}")
							showCars.append(_car["carId"])
				if numbers is not None and len(numbers) > 0:
					for carId, _car in cars.items():
						if _car["number"] in numbers:
							showCars.append(carId)
				if len(showCars) == 0:
					showCars = list(cars.keys())
				showCars = list(set(showCars))
				#print("showCars")
				#Dest.json.print(showCars)

				# calculate the average laptime for each car and set that to the first lap
				for carId in showCars:
					print(f"carId: {carId} as {type(carId)}")
					lapTimes:list[int] = []
					for _lap, _cars in enumerate(race["laps"]):
						if _lap == 0:
							continue
						for _car in _cars:
							if _car["carId"] not in showCars:
								continue
							if _car["carId"] == carId:
								lapTimes.append(_car["time"])
					#print("lapTimes:")
					#Dest.json.print(lapTimes)
					carAvgLaptime[carId] = sum(lapTimes) / len(lapTimes)
				print("carAvgLaptime")
				Dest.json.print(carAvgLaptime)

				# prepare the data for the graph
				for _lap, _cars in enumerate(race["laps"]):
					if _lap == 0:
						for _car in _cars:
							team = cars.get(_car["carId"], {})
							if _car["carId"] not in showCars:
								continue
							average = carAvgLaptime[_car["carId"]]
							x.append(_lap + 1)
							y.append(average)
							yTxt.append(ACC.convertTime(average))
							car.append(
								f"#{team['number']} {ACC.carTeam(team)}"
							)
						continue
					for _car in _cars:
						team = cars.get(_car["carId"], {})
						# check if the carId is in the showCars list
						if _car["carId"] not in showCars:
							continue
						x.append(_lap + 1)
						y.append(_car["time"])
						yTxt.append(ACC.convertTime(_car["time"]))
						car.append(
							f"#{team['number']} {ACC.carTeam(team)}"
						)
						if _car["time"] > slowest_laptime_ms:
							slowest_laptime_ms = _car["time"]
						if _car["time"] < fastest_laptime_ms:
							fastest_laptime_ms = _car["time"]

				# create a dataframe
				df = pd.DataFrame({
					"lap": x,
					"laptime_ms": y,
					"laptime": yTxt,
					"car": car,
				})
				fig = px.line(
					df,
					x = "lap",
					y = "laptime_ms",
					color = "car",
					title = f"{race['session']['name']} · {race['session']['track']['name']} · {race['session']['type']['name']}"\
						f" · {race['session']['laps']} laps{' (wet)' if race['session']['wet'] == 1 else ''}"\
						f" · {session['info']['datetime'].strftime('%m-%d-%y @%H')}",
					labels = {
						"laptime_ms": label["laptime"],
						"lap": label["laps"],
						"car": label["drivers"],
					},
					markers = True,
				)
				self.fig_line_update_defaults(fig, config, race)
				# add a gray box on the first lap
				fig.add_vrect(
					x0 = min(x),
					x1 = min(x) + 1,
					fillcolor = "rgb(64,64,64)",
					opacity = 0.2,
					layer = "below",
					line_width = 0,
				),
				fig.add_annotation(
					x = min(x) + 0.5,
					# get the middle of the y axis
					#y = (fastest_laptime_ms + (slowest_laptime_ms - fastest_laptime_ms) / 2) + 4000,
					y = (fastest_laptime_ms + slowest_laptime_ms) / 2,
					text = label["bug_start_laptimes"],
					showarrow = False,
					textangle = -90,
					font = dict(
						color = "rgba(96,96,96,0.5)",
						size = 30
					),
				)
				yTickvals = [fastest_laptime_ms + (slowest_laptime_ms - fastest_laptime_ms) / 10 * i for i in range(11)]
				fig.update_layout(
					xaxis = dict(
						# set range to 1 to laps
						range = [1, race['session']['laps']],
					),
					yaxis = dict(
						tickmode = "array",
						tickvals = yTickvals,
						ticktext = [ACC.convertTime(v) for v in yTickvals],
					)
				)
				# slowest lap annotation
				slowest_laptime_position = y.index(slowest_laptime_ms)
				fig.add_annotation(
					x = df['lap'][slowest_laptime_position],
					y = df['laptime_ms'][slowest_laptime_position],
					text = f"{ACC.convertTime(slowest_laptime_ms)}",
					showarrow = True,
					arrowhead = 1,
					arrowwidth = 3,
					arrowcolor = config['annotation']['slowest']['color'],
					font = dict(
						color = config['annotation']['slowest']['color'],
						size = config['annotation']['slowest']['size']
					),
					ax = -15,
					ay = -30,
				)
				# fastest lap annotation
				fastest_laptime_position = y.index(fastest_laptime_ms)
				fig.add_annotation(
					x = df['lap'][fastest_laptime_position],
					y = df['laptime_ms'][fastest_laptime_position],
					text = f"{ACC.convertTime(fastest_laptime_ms)}",
					showarrow = True,
					arrowhead = 1,
					arrowwidth = 3,
					arrowcolor = config['annotation']['fastest']['color'],
					font = dict(
						color = config['annotation']['fastest']['color'],
						size = config['annotation']['fastest']['size']
					),
					ax = 15,
					ay = 30,
				)
				# average laptime
				average_laptime_ms = sum(y) / len(y)
				fig.add_shape(
					type = "line",
					x0 = 1,
					y0 = average_laptime_ms,
					x1 = race['session']['laps'],
					y1 = average_laptime_ms,
					line = dict(
						color = "rgb(192,192,192)",
						width = 2,
						dash = "dot",
					),
				)
				fig.write_image(
					Dest.join(temp, pngFile)
				)
				# send the png
				await ctx.send(
					file=discord.File(
						Dest.join(temp, pngFile)
					)
				)
				Dest.json.save(
					Dest.join(temp, f"{dt.strftime('%y%m%d')}_{dt.strftime('%H%M%S')}_{heat}.result.laptimes.json"),
					{
						"x": x,
						"y": y,
						"yTxt": yTxt,
						"car": car,
					}
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
		description = "Show a graph of drivers positions throughout a race",
		usage = "positions [input with date and time or latest and maybe type of the race and]",
		hidden = True,
		aliases = [
			"position",
			"laps",
		]
	)
	@commands.guild_only()
	@commands.has_permissions(moderate_members=True)
	async def positions(self, ctx:commands.Context, *, input:str = None) -> None:
		"""
		Show a graph of drivers position
		```
		{ctx.prefix}positions
		{ctx.prefix}positions latest
		{ctx.prefix}positions 241231
		{ctx.prefix}positions 241231 235959
		```
		"""
		try:
			async with ctx.typing():
				date, time, _, _, _ = ACC.parseRaceInput(input)
				print(f"positions date: {date}\ntime: {time}")
				temp = self.bot.getTemp("results")
				session = ACC.session(
					temp,
					date,
					time,
					free_practices=0,
				)
				if session is None:
					raise ValueError("No results found for the given date (and time).")
				dt = session.get("info", {}).get("datetime", None)
				if dt is None:
					raise ValueError("No datetime found in session info.")
				# get date and time and session from filename: 240309_220433_R.json.result.json
				file = f"{dt.strftime('%y%m%d')}_{dt.strftime('%H%M%S')}_R.result.json"
				pngFile = Dest.extension(
					Dest.suffix(
						Dest.filename(file),
						'.laptimes'
					), 'png'
				)
				print(f"pngFile: {pngFile}")
				# check if png file exists
				"""
				if Dest.exists(Dest.join(temp, pngFile)):
					return await ctx.send(
						file=discord.File(
							Dest.join(temp, pngFile)
						)
					)
				"""
				# prepare the graph
				label = self.bot.getConfig(ctx.guild, "label", "graph")
				config = self.bot.getConfig(ctx.guild, "graph")
				race = session.get("r")
				quali = session.get("q")
				print("session info")
				Dest.json.print(session.get("info"))
				# check
				if len(race.get("laps", [])) == 0:
					# delete the race file
					Dest.remove(file)
					raise ValueError(f"No laps found, no data to graph...")
				x = []
				y = []
				car = []
				cars = race.get("cars", {})
				for _lap, lap in enumerate(race["laps"]):
					# if _lap is zero, then get the starting positions from quali results
					if _lap == 0 and quali is not None and len(quali.get("positions", [])) > 0:
						for position, _car in enumerate(quali.get("positions", [])):
							x.append(_lap + 1)
							y.append(position + 1)
							car.append(
								f"#{cars.get(_car['carId'], {}).get('number', '0')} {ACC.carTeam(cars.get(_car['carId']))}",
							)
						continue
					# get
					for position, _car in enumerate(lap):
						x.append(_lap + 1) # _car["lap"]
						y.append(position + 1) # _car["position"]
						car.append(
							f"#{cars.get(_car['carId'], {}).get('number', '0')} {ACC.carTeam(cars.get(_car['carId']))}",
						)
				df = pd.DataFrame({
					"lap": x,
					"position": y,
					"car": car,
				})
				fig = px.line(
					df,
					x = "lap",
					y = "position",
					color = "car",
					title = f"{race['session']['name']} · {race['session']['track']['name']} · {race['session']['type']['name']}"\
						f" · {race['session']['laps']} laps{' (wet)' if race['session']['wet'] == 1 else ''}"\
						f" · {session['info']['datetime'].strftime('%m-%d-%y @%H')}",
					labels = {
						"position": label["positions"],
						"lap": label["laps"],
						"car": label["drivers"],
					}
				)
				self.fig_line_update_defaults(fig, config, race)
				fig.add_vrect(
					x0 = min(x),
					x1 = min(x) + 1,
					fillcolor = "rgb(64,64,64)",
					opacity = 0.2,
					layer = "below",
					line_width = 0,
				),
				fig.add_annotation(
					x = min(x) + 0.5,
					# get the middle of the y axis
					y = (max(y) + min(y)) / 2,
					text = label["bug_start_positions"],
					showarrow = False,
					textangle = -90,
					font = dict(
						color = "rgba(96,96,96,0.5)",
						size = 30
					),
				)
				fig.update_layout(
					yaxis = dict(
						autorange = "reversed",
					)
				)
				fig.write_image(
					Dest.join(temp, pngFile)
				)
				# send the png
				await ctx.send(
					file=discord.File(
						Dest.join(temp, pngFile)
					)
				)
				Dest.json.save(
					Dest.join(temp, f"{dt.strftime('%y%m%d')}_{dt.strftime('%H%M%S')}_R.result.positions.json"),
					{
						"x": x,
						"y": y,
						"car": car,
					}
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

async def setup(bot:bang.Bot) -> None:
	try:
		await bot.add_cog(
			Graph(
				bot
			)
		)
	except Exception as e:
		raise e

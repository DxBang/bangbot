import discord
from discord.ext import commands
import traceback
import re
import plotly.express as px
import pandas as pd
import base64
from bang.acc import ACC
from bang.dest import Dest


class Graph(commands.Cog, name="Graph"):
	__slots__ = (
		"bot",
		"ftp",
	)
	def __init__(self, bot:commands.Bot) -> None:
		try:
			self.bot = bot
		except Exception as e:
			raise e

	def parse_graph_input(self, input:str = None) -> tuple[str, str, str, list[int]|None, int|None]:
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
			print(f"input: {input}")
			if date is None:
				date = ACC.parse_date_for_regexp(input, False)
				print(f"	date: {date}")
				if date is not None:
					continue
			if date is not None and time is None:
				time = ACC.parse_time_for_regexp(input, False)
				print(f"	time: {time}")
				if time is not None:
					continue
			if input.lower() in ["r", "q", "fp", "f"]:
				print(f"	session: {input}")
				if input.lower() == "f":
					session = "FP"
				else:
					session = input.upper()
				continue
			if input.startswith("#"):
				print(f"	number: {input}")
				number = int(input.replace("#", ""))
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
			date = "\d{6}"
			print(f"date: {date}")
		if time is None:
			time = "\d{6}"
			print(f"time: {time}")
			# check if input is a car number
		if number is not None:
			top = None
		return date, time, session, top, number

	@commands.command(
		description = "Show a graph of drivers lap times",
		usage = "laptime [input with date and time or latest and maybe type of the race and #car number or 1-10 for top 10]",
		hidden = False,
		aliases = [
			"laptime",
		]
	)
	@commands.guild_only()
	async def laptimes(self, ctx:commands.Context, *, input:str = None) -> None:
		"""
		Show a graph of drivers lap times
		```
		{ctx.prefix}laptime 241231 235959 r
		{ctx.prefix}laptime q 241231 235959
		{ctx.prefix}laptime fp 241231 235959
		{ctx.prefix}laptime latest
		{ctx.prefix}laptime latest r 1-10
		{ctx.prefix}laptime r latest #21
		{ctx.prefix}laptime 241231 235959 q 5-10
		{ctx.prefix}laptime 241231 235959 f #21
		```
		"""
		try:
			print(f"graph")
			async with ctx.typing():
				# check if input is a date
				config = self.bot.get_config(ctx.guild, "graph")
				label = self.bot.get_config(ctx.guild, "label", "graph")
				date, time, session, top, number = self.parse_graph_input(input)
				print(f"\ndate: {date}\ntime: {time}\nsession: {session}\ntop: {top}\nnumber: {number}\n")
				# get the results from temp result directory
				temp = self.bot.get_temp("results")
				regexp = f"^{date}_{time}_{session}\.result\.json$"
				print(f"regexp: {regexp}")
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
				pngFile = f"{date}_{time}_{session}_{_top}_{_number}.laptimes.png"
				print(f"pngFile: {pngFile}")
				# check if png file exists

				if Dest.exists(Dest.join(temp, pngFile)):
					return await ctx.send(
						file=discord.File(
							Dest.join(temp, pngFile)
						)
					)

				# load the result sa json
				result = Dest.json.load(resultFile, True)
				if len(result['laps']) == 0:
					# delete the result file
					Dest.remove(resultFile)
					raise ValueError(f"No laps found, no data to graph...")
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
							laptime = ACC.convert_time(laptime_ms)
							if slowest_laptime_ms < laptime_ms:
								slowest_laptime_ms = laptime_ms
							if fastest_laptime_ms > laptime_ms:
								fastest_laptime_ms = laptime_ms
							data.append({
								"driver": f"#{car['number']} {ACC.driverName(driver)}",
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
				wet = "".join(["&#" + str(ord(char)) + ";" for char in "🌧️"])
				df = pd.DataFrame(data)
				# create a figure and axis
				fig = px.line(
					df,
					x = "lap",
					y = "laptime_ms",
					line_shape = "spline",
					color = "driver",
					title = f"{result['server']} · {ACC.fullTrackName(result['track'])} · {result['typeName']} · {result['session']['laps']} laps {wet if result['wet'] == 1 else ''}",
					labels = {
						"laptime_ms": label['laptime'],
						"lap": label["laps"],
						"driver": label["drivers"],
					},
					markers = True,
					template = config['template'],
					range_x = [1, result['session']['laps']],
				)
				width = max(config['lap_width'] * result['session']['laps'] + 400, config['min_width'])
				height = config['min_height']
				ytickvals = [fastest_laptime_ms + (slowest_laptime_ms - fastest_laptime_ms) / 10 * i for i in range(11)]
				fig.update_layout(
					xaxis = dict(
						tickmode = 'linear',
						title = dict(
							font = dict(
								size = config['label']['size'],
							)
						)
					),
					yaxis = dict(
						tickmode = 'array',
						tickvals = ytickvals,
						ticktext = [ACC.convert_time(tickval) for tickval in ytickvals],
						title = dict(
							font = dict(
								size = config['label']['size'],
							)
						),
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
				)
				fig.update_traces(
					line = {
						'width': 5,
					}
				)
				slowest_laptime_position = df[df['laptime_ms'] == slowest_laptime_ms].index[0]
				fastest_laptime_position = df[df['laptime_ms'] == fastest_laptime_ms].index[0]
				fig.add_annotation(
					x = df['lap'][slowest_laptime_position],
					y = df['laptime_ms'][slowest_laptime_position],
					text = f"{ACC.convert_time(slowest_laptime_ms)}",
					showarrow = True,
					arrowhead = 1,
					arrowwidth = 3,
					arrowcolor = config['annotation']['slowest']['color'],
					font = dict(
						color = config['annotation']['slowest']['color'],
						size = config['annotation']['slowest']['size']
					),
					ax = -20,
					ay = -40,
				)
				fig.add_annotation(
					x = df['lap'][fastest_laptime_position],
					y = df['laptime_ms'][fastest_laptime_position],
					text = f"{ACC.convert_time(fastest_laptime_ms)}",
					showarrow = True,
					arrowhead = 1,
					arrowwidth = 3,
					arrowcolor = config['annotation']['fastest']['color'],
					font = dict(
						color = config['annotation']['fastest']['color'],
						size = config['annotation']['fastest']['size']
					),
					ax = 20,
					ay = 40,
				)
				average_laptime_ms = sum([lap['laptime_ms'] for lap in data]) / len(data)
				# create a highlight for average laptime
				fig.add_shape(
					type = "line",
					x0 = 1,
					y0 = average_laptime_ms,
					x1 = result['session']['laps'],
					y1 = average_laptime_ms,
					line = dict(
						color = "rgb(192,192,192)",
						width = 2,
						dash = "dot",
					),
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
		description = "Show a graph of drivers positions throughout a race",
		usage = "positions [input with date and time or latest and maybe type of the race and]",
		hidden = False,
		aliases = [
			"position",
			"laps",
		]
	)
	@commands.guild_only()
	async def positions(self, ctx:commands.Context, *, input:str = None) -> None:
		"""
		Show a graph of drivers position
		```
		{ctx.prefix}positions 241231 235959 r
		{ctx.prefix}positions 241231 235959 q
		{ctx.prefix}positions 241231 235959 fp
		{ctx.prefix}positions latest
		{ctx.prefix}positions latest r 1-10
		{ctx.prefix}positions latest r #21
		{ctx.prefix}positions 241231 235959 q 5-10
		{ctx.prefix}positions 241231 235959 fp #21
		```
		"""
		try:
			print(f"position")
			async with ctx.typing():
				# check if input is a date
				config = self.bot.get_config(ctx.guild, "graph")
				label = self.bot.get_config(ctx.guild, "label", "graph")
				date, time, session, _, _ = self.parse_graph_input(input)
				print(f"\ndate: {date}\ntime: {time}\nsession: {session}\n")
				temp = self.bot.get_temp("results")
				regexp = f"^{date}_{time}_{session}\.result\.json$"
				print(f"regexp: {regexp}")
				resultFile = Dest.scan(temp, regexp, 'last')
				if resultFile is None:
					raise ValueError("No results found. Run the race, qualify or practice command first.")
				# get date and time and session from filename: 240309_220433_R.json.result.json
				filename = Dest.filename(resultFile)
				print(f"filename: {filename}")
				date, time, session = filename.split(".")[0].split("_")
				print(f"date: {date}\ntime: {time}\nsession: {session}")
				# get the results from temp result directory
				jsonFile = f"{date}_{time}_{session}.json"
				print(f"jsonFile: {jsonFile}")
				pngFile = f"{date}_{time}_{session}.positions.png"
				print(f"pngFile: {pngFile}")
				# check if png file exists

				if Dest.exists(Dest.join(temp, pngFile)):
					return await ctx.send(
						file=discord.File(
							Dest.join(temp, pngFile)
						)
					)

				# load the result sa json
				result = Dest.json.load(resultFile, True)
				if len(result['laps']) == 0:
					# delete the result file
					Dest.remove(resultFile)
					raise ValueError(f"No laps found, no data to graph...")
				cars:dict = {}
				carLaps:dict = {}
				carTime:dict = {}
				for carId, car in result.get("cars", {}).items():
					carId = int(carId)
					carLaps.setdefault(carId, 0)
					carTime.setdefault(carId, 0)
					# create the drivers dict for each car and use driverIndex as key
					drivers:dict = {}
					for driver_index, driver in car.get("drivers").items():
						driver_index = int(driver_index)
						_driver:dict = {
							"playerId": driver["playerId"],
							"firstName": driver["firstName"],
							"lastName": driver["lastName"],
							"shortName": driver["shortName"],
						}
						drivers[driver_index] = _driver
					_car:dict = {
						"car": car["car"],
						"number": car["number"],
						"laps": car["laps"],
						"time": car["time"],
						"drivers": drivers,
					}
					cars[carId] = _car
				laps = [[] for _ in range(max([car.get("laps") for car in cars.values()]))]
				for lap in result.get("laps", []):
					car_id:int = lap["carId"]
					driver_index:int = lap["driverIndex"]
					laptime:int = lap["laptime"]
					if carLaps.get(car_id) == 0:
						carLaps[car_id] += 1
						continue
					l = carLaps[car_id]
					idx = l - 1
					carTime[car_id] += laptime
					_lap = {
						"position": 0, #len(laps[idx]) + 1 if idx in laps else 1,
						"lap": l,
						"carId": car_id,
						"driverIndex": driver_index,
						"laptime": laptime,
						"time": carTime.get(car_id),
					}
					laps[idx].append(_lap)
					carLaps[car_id] += 1
				for l, lap_list in enumerate(laps):
					laps[l] = sorted(lap_list, key=lambda x: x["time"])
					# fix position
					for i, lap in enumerate(laps[l]):
						lap["position"] = i + 1
				x = []
				y = []
				car = []
				for _lap, lap in enumerate(laps):
					for position, _car in enumerate(lap):
						x.append(_lap) # _car["lap"]
						y.append(position + 1) # _car["position"]
						car.append(
							f"#{cars.get(_car['carId'], {}).get('number', '0')} {ACC.driverName(cars.get(_car['carId']).get('drivers', {}).get(_car['driverIndex'], {}))}",
							#f"#{cars.get(_car['carId'], {}).get('number', 'N/A')} {cars.get(_car['carId']).get('drivers', {}).get(_car['driverIndex'], {}).get('lastName', 'N/A')}"
						)
				wet = "".join(["&#" + str(ord(char)) + ";" for char in "🌧️"])
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
					line_shape = "spline",
					template = "plotly_dark",
					title = f"{result['server']} · {ACC.fullTrackName(result['track'])} · {result['typeName']} · {result['session']['laps']} laps {wet if result['wet'] == 1 else ''}",
					labels = {
						"position": label["positions"],
						"lap": label["laps"],
						"car": label["drivers"],
					},
				)
				width = max(config['lap_width'] * result['session']['laps'] + 400, config['min_width'])
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
						autorange = "reversed",
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
				)
				fig.update_traces(
					line = {
						'width': 5,
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

async def setup(bot:commands.Bot) -> None:
	try:
		await bot.add_cog(
			Graph(
				bot
			)
		)
	except Exception as e:
		raise e

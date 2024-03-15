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
			if input.lower() == "latest":
				date = "\d{6}"
				time = "\d{6}"
				session = '(R|Q|FP)'
			else:
				# check if input is a date
				date = ACC.parse_date_for_regexp(input, False)
				# check if input is a time
				time = ACC.parse_time_for_regexp(input, False)
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
					# delete the result file
					Dest.remove(resultFile)
					raise ValueError(f"No laps found, no data to graph...")
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
							laptime = ACC.convert_time(laptime_ms)
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
					title = f"{result['server']} · {ACC.fullTrackName(result['track'])} · {result['typeName']} · {result['session']['laps']} laps",
					labels = {
						"laptime_ms": "Laptime",
						"lap": "Laps",
						"driver": "Drivers",
					},
					markers = True,
					template = config['template'],
					range_x = [1, result['session']['laps']],
				)
				width = max(config['lap_spacing'] * result['session']['laps'] + 400, config['min_width'])
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

async def setup(bot:commands.Bot) -> None:
	try:
		await bot.add_cog(
			Graph(
				bot
			)
		)
	except Exception as e:
		raise e

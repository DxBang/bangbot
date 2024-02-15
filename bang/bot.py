import sys, os, traceback
import json
import discord
from discord.ext import commands
from discord import app_commands

from datetime import datetime, timedelta, timezone

class Bang(commands.Bot):
	__slots__ = (
		"config",
		"data",
		"sql",
	)

	def __init__(self):
		try:
			with open("config.json") as f:
				self.config = json.load(f)
			self.data = None
			self.sql = None
		except FileNotFoundError:
			print("config.json not found.")
			sys.exit(1)
		except json.JSONDecodeError:
			print("config.json is invalid.")
			sys.exit(1)
		except Exception as e:
			traceback.print_exc()
			sys.exit(1)
			



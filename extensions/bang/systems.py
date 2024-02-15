import aiomysql
import asyncio
import discord
import json
import os
import re

class Systems:
	def __init__(self, config):
		self.config = config
		return
	
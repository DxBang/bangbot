"""

Login to GPortal via FTP and get the race results.

"""

import os
import json
import ftplib
import datetime

class GPortal:
	def __init__(self, config):
		self.config = config
		self.ftp = ftplib.FTP(config['host'])
		self.ftp.login(config['user'], config['password'])
		self.ftp.cwd(config['path'])

	def get_results(self):
		return

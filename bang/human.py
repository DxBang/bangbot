from datetime import datetime, timezone, timedelta
import re
from dateutil import parser


class Human:
	separator = dict(
		date = r"[.-\/]?",
		time = r"[.:]?",
	)
	@staticmethod
	def date(date:str = None) -> datetime | str:
		try:
			if isinstance(date, datetime):
				return date
			if date is None or date.lower() in ["today", "latest", "last"]:
				return datetime.now(
					timezone.utc
				).replace(
					hour=23,
					minute=59,
					second=59
				)
			if date.lower() in ['*', 'all', 'full', 'complete', 'any']:
				return '*'
			if date.lower() == "now":
				return datetime.now(
					timezone.utc
				)
			if date.lower() == "yesterday":
				return datetime.now(
					timezone.utc
				).replace(
					hour=23,
					minute=59,
					second=59
				) - timedelta(days=1)
			if date.lower() == "tomorrow":
				return datetime.now(
					timezone.utc
				).replace(
					hour=23,
					minute=59,
					second=59
				) + timedelta(days=1)
			sep = Human.separator["date"]
			# 1999/12/31
			if re.match(rf"^[1-2][0-9][0-9]{{2}}{sep}[0-1][0-9]{sep}[0-3][0-9]$", date):
				return datetime.strptime(
					re.sub(sep[:-1], "", date),
					"%Y%m%d",
				).replace(
					hour=23,
					minute=59,
					second=59
				)
			# 99/12/31
			if re.match(rf"^[0-9]{{2}}{sep}[0-1][0-9]{sep}[0-3][0-9]$", date):
				return datetime.strptime(
					re.sub(sep[:-1], "", date),
					"%y%m%d",
				).replace(
					hour=23,
					minute=59,
					second=59
				)
			# 31/12/1999
			if re.match(rf"^[0-3]?[0-9]{sep}[0-1]?[0-9]{sep}[1-2][0-9]{3}$", date):
				return datetime.strptime(
					re.sub(sep[:-1], "", date),
					"%d%m%Y",
				).replace(
					hour=23,
					minute=59,
					second=59
				)
			# 31/12
			if re.match(rf"^[0-3]?[0-9]{sep}[0-1]?[0-9]$", date):
				return datetime.strptime(
					re.sub(sep[:-1], "", date),
					"%d%m",
				).replace(
					hour=23,
					minute=59,
					second=59,
					year=datetime.now().year
				)
			# all failed... try the parser
			return parser.parse(
				date
			)
		except Exception as e:
			raise e

	@staticmethod
	def time(time:str = None) -> datetime | str:
		try:
			if isinstance(time, datetime):
				return time
			if time is None or time.lower() in ["today", "latest", "last"]:
				return datetime.now(
					timezone.utc
				).replace(
					hour=23,
					minute=59,
					second=59
				)
			if time.lower() in ['*', 'all', 'full', 'complete', 'any']:
				return '*'
			if time.lower() == "now":
				return datetime.now(
					timezone.utc
				)
			sep = Human.separator["time"]
			if re.match(rf"^[0-2][0-9]{sep}[0-5][0-9]{sep}[0-5][0-9]$", time):
				return datetime.strptime(
					re.sub(sep[:-1], "", time),
					"%H%M%S"
				)
			if re.match(rf"^[0-2][0-9]{sep}[0-5][0-9]$", time):
				return datetime.strptime(
					re.sub(sep[:-1], "", time),
					"%H%M"
				).replace(
					second=59
				)
			if re.match(r"^[0-2][0-9]$", time):
				return datetime.strptime(
					time,
					"%H"
				).replace(
					minute=59,
					second=59
				)
			return parser.parse(
				time
			)
		except Exception as e:
			raise e

	@staticmethod
	def parseBool(value:str) -> bool:
		if isinstance(value, bool):
			return value
		if value.lower() in ["true", "yes", "1"]:
			return True
		if value.lower() in ["false", "no", "0"]:
			return False
		return False

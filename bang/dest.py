import os
import tempfile
import shutil
import json
import re
from typing import Literal

class Dest:
	@staticmethod
	def info(destination:str) -> tuple[str, str, str, str]:
		try:
			dir, base = os.path.split(destination)
			name, ext = os.path.splitext(base)
			return dir, base, name, ext
		except Exception as e:
			raise e

	@staticmethod
	def filename(destination:str) -> str:
		try:
			_, base = os.path.split(destination)
			name, _ = os.path.splitext(base)
			return name
		except Exception as e:
			raise e

	@staticmethod
	def base(destination:str) -> str:
		try:
			_, base = os.path.split(destination)
			return base
		except Exception as e:
			raise e

	@staticmethod
	def basename(destination:str) -> str:
		return Dest.base(destination)

	@staticmethod
	def extension(destination:str, extension:str = None) -> str:
		try:
			if extension is None:
				_, base = os.path.split(destination)
				_, ext = os.path.splitext(base)
				return ext[1:]
			path, base = os.path.split(destination)
			name, _ = os.path.splitext(base)
			return os.path.join(
				path,
				f"{name}.{extension}"
			)
		except Exception as e:
			raise e

	@staticmethod
	def dir(destination:str) -> str:
		try:
			dir, _ = os.path.split(destination)
			return dir
		except Exception as e:
			raise e

	@staticmethod
	def join(*args) -> str:
		try:
			return os.path.join(*args)
		except Exception as e:
			raise e

	@staticmethod
	def exists(destination:str) -> bool:
		try:
			return os.path.exists(destination)
		except Exception as e:
			raise e

	@staticmethod
	def isfile(destination:str) -> bool:
		try:
			return os.path.isfile(destination)
		except Exception as e:
			raise e

	@staticmethod
	def isdir(destination:str) -> bool:
		try:
			return os.path.isdir(destination)
		except Exception as e:
			raise e

	@staticmethod
	def mkdir(path:str) -> None:
		try:
			os.makedirs(path, exist_ok=True)
		except Exception as e:
			raise e

	@staticmethod
	def remove(destination:str) -> None:
		try:
			os.remove(destination)
		except Exception as e:
			raise e

	@staticmethod
	def delete(destination:str) -> None:
		return Dest.remove(destination)

	@staticmethod
	def rename(source:str, destination:str) -> None:
		try:
			os.rename(source, destination)
		except Exception as e:
			raise e

	@staticmethod
	def move(source:str, destination:str) -> None:
		return Dest.rename(source, destination)

	@staticmethod
	def copy(source:str, destination:str) -> None:
		try:
			shutil.copy(source, destination)
		except Exception as e:
			raise e

	@staticmethod
	def temp(system:bool=True, subfolder:str = None) -> str:
		try:
			if system is not None and system is True:
				temp = tempfile.gettempdir()
			else:
				temp = os.path.join(
					os.getcwd(),
					"tmp"
				)
			if subfolder is not None:
				temp = os.path.join(
					temp,
					subfolder
				)
			if not os.path.exists(temp):
				os.makedirs(temp)
			return temp
		except Exception as e:
			raise e

	@staticmethod
	def current() -> str:
		try:
			return os.getcwd()
		except Exception as e:
			raise e

	@staticmethod
	def home() -> str:
		try:
			return os.path.expanduser("~")
		except Exception as e:
			raise e

	@staticmethod
	def parent(path:str) -> str:
		try:
			return os.path.dirname(path)
		except Exception as e:
			raise e

	@staticmethod
	def backup(file:str) -> str:
		try:
			dir, base = os.path.split(file)
			name, ext = os.path.splitext(base)
			return os.path.join(
				dir,
				f"{name}.backup{ext}"
			)
		except Exception as e:
			raise e

	@staticmethod
	def prefix(file:str, prefix:str) -> str:
		try:
			dir, base = os.path.split(file)
			name, ext = os.path.splitext(base)
			return os.path.join(
				dir,
				f"{prefix}{name}{ext}"
			)
		except Exception as e:
			raise e

	@staticmethod
	def suffix(file:str, suffix:str) -> str:
		try:
			dir, base = os.path.split(file)
			name, ext = os.path.splitext(base)
			return os.path.join(
				dir,
				f"{name}{suffix}{ext}"
			)
		except Exception as e:
			raise e

	@staticmethod
	def file(file:str) -> str:
		try:
			# use os.path.abspath to get the absolute path with the correct directory separator
			return os.path.abspath(file)
		except Exception as e:
			raise e

	@staticmethod
	def mime(file:str) -> str:
		try:
			_, ext = os.path.splitext(file)
			return {
				".txt": "text/plain",
				".html": "text/html",
				".css": "text/css",
				".js": "text/javascript",
				".json": "application/json",
				".png": "image/png",
				".jpg": "image/jpg",
				".jpeg": "image/jpg",
				".gif": "image/gif",
				".mp3": "audio/mpeg",
				".mp4": "video/mp4",
				".ogg": "audio/ogg",
				".ogv": "video/ogg",
				".webm": "video/webm",
				".pdf": "application/pdf",
				".zip": "application/zip",
				".tar": "application/x-tar",
				".gz": "application/gzip",
				".7z": "application/x-7z-compressed",
			}.get(ext, "application/octet-stream")
		except Exception as e:
			raise e

	@staticmethod
	def scan(path:str, regexp:re, mode:Literal['all', 'first', 'last'] = 'all') -> list[str] | str | None:
		try:
			if mode == 'all':
				return [
					os.path.join(path, file)
					for file in os.listdir(path)
					if re.match(regexp, file)
				]
			if mode == 'first':
				for file in os.listdir(path):
					if re.match(regexp, file):
						return os.path.join(path, file)
			if mode == 'last':
				files = os.listdir(path)
				files.reverse()
				for file in files:
					if re.match(regexp, file):
						return os.path.join(path, file)
		except Exception as e:
			raise e

	@staticmethod
	def scan_next(path:str, first:re, next:re) -> str | None:
		try:
			files = os.listdir(path)
			found = False
			for file in files:
				if re.match(first, file):
					print(f"first: {file}")
					found = True
					continue
				if found and re.match(next, file):
					print(f"next: {file}")
					return os.path.join(path, file)
		except Exception as e:
			raise e

	@staticmethod
	def scan_prev(path:str, first:re, prev:re) -> str | None:
		try:
			files = os.listdir(path)
			files.reverse()
			found = False
			for file in files:
				if found is False and re.match(first, file):
					print(f"first: {file}")
					found = True
					continue
				if found is True and re.match(prev, file):
					print(f"prev: {file}")
					return os.path.join(path, file)
		except Exception as e:
			raise e

	@staticmethod
	def open(path:str) -> list[str]:
		try:
			return os.listdir(path)
		except Exception as e:
			raise e

	@staticmethod
	def load(file:str) -> str:
		try:
			with open(file, "r+") as f:
				return f.read()
		except Exception as e:
			raise e

	@staticmethod
	def save(file:str, content:str) -> None:
		try:
			with open(file, "w+") as f:
				f.write(content)
		except Exception as e:
			raise e

	@staticmethod
	def append(file:str, content:str) -> None:
		try:
			with open(file, "a+") as f:
				f.write(content)
		except Exception as e:
			raise e

	class binary:
		@staticmethod
		def load(file:str) -> bytes:
			try:
				with open(file, "rb+") as f:
					return f.read()
			except Exception as e:
				raise e

		@staticmethod
		def save(file:str, data:bytes) -> None:
			try:
				with open(file, "wb+") as f:
					f.write(data)
			except Exception as e:
				raise e

		@staticmethod
		def append(file:str, data:bytes) -> None:
			try:
				with open(file, "ab+") as f:
					f.write(data)
			except Exception as e:
				raise e

	class json:
		@staticmethod
		def read(string:str, convert:bool = False, int_key:bool = True) -> dict:
			try:
				if convert is True:
					return Dest.json.convert(
						json.loads(string),
						int_key
					)
				return json.loads(string)
			except Exception as e:
				raise e

		@staticmethod
		def load(file:str, convert:bool = False, int_key:bool = True) -> dict:
			try:
				if convert is True:
					return Dest.json.convert(
						Dest.json.load(file),
						int_key
					)
				with open(file, "rb+") as f:
					return json.load(f)
			except Exception as e:
				raise e

		@staticmethod
		def convert(data, int_key:bool = True) -> dict|list|str|int|float:
			try:
				ret = None
				if type(data) is dict:
					ret:dict = {}
					for key, value in data.items():
						if int_key is True and key.isdigit() and str(int(key)) == key:
							key = int(key)
						ret[key] = Dest.json.convert(value, int_key)
				elif type(data) is list:
					ret:list = []
					for value in data:
						ret.append(Dest.json.convert(value, int_key))
				else:
					ret = data
				return ret
			except Exception as e:
				raise e

		@staticmethod
		def save(file:str, data) -> None:
			try:
				with open(file, "w+") as f:
					json.dump(data, f, indent='\t')
			except Exception as e:
				raise e

		@staticmethod
		def print(data) -> None:
			try:
				print(
					json.dumps(
						data,
						indent=4,
						default=str
					)
				)
			except Exception as e:
				raise e

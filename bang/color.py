class Color:
	def __init__(self, h:int, s:float, l:float):
		self.h = h
		self.s = s
		self.l = l

	def __str__(self):
		return self.get_hsl()

	@classmethod
	def guess(cls, string:str):
		if string.startswith("#"):
			return cls.from_hex(string)
		elif string.startswith("rgb("):
			return cls.from_rgb(*map(int, string[4:-1].split(",")))
		elif string.startswith("hsl("):
			return cls.from_hsl(*map(float, string[4:-1].split(",")))
		else:
			raise ValueError("Invalid color string")


	@classmethod
	def from_hsl(cls, h:int, s:float, l:float):
		return cls(h, s, l)

	@classmethod
	def from_rgb(cls, r:int, g:int, b:int) -> tuple:
		print(f"from_rgb: {r}, {g}, {b}")
		h, s, l = cls.rgb_to_hsl(r, g, b)
		return cls(h, s, l)

	@classmethod
	def from_hex(cls, hex:str):
		pass

	@staticmethod
	def rgb_to_hsl(r:int, g:int, b:int) -> tuple:
		r, g, b = r / 255.0, g / 255.0, b / 255.0
		max_val = max(r, g, b)
		min_val = min(r, g, b)
		diff = max_val - min_val
		l = (max_val + min_val) / 2
		if max_val == min_val:
			h = s = 0
		else:
			s = diff / (2 - max_val - min_val) if l > 0.5 else diff / (max_val + min_val)
			if max_val == r:
				h = (g - b) / diff + (6 if g < b else 0)
			elif max_val == g:
				h = (b - r) / diff + 2
			else:
				h = (r - g) / diff + 4
			h /= 6
		return int(h * 360), float(s), float(l)

	def adjust_lightness(self, delta:float):
		self.l = max(0, min(1, self.l + delta))
		return self

	def adjust_saturation(self, delta:float):
		self.s = max(0, min(1, self.s + delta))
		return self

	def get_hsl(self) -> str:
		return f"hsl({self.h},{self.s},{self.l})"

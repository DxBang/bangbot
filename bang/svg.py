
class SVG:
	@staticmethod
	def emoji(emoji:str):
		"""Return SVG for the given emoji."""
		return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64"><text x="50%" y="50%" font-size="64" text-anchor="middle" dominant-baseline="middle">{emoji}</text></svg>'


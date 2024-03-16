
class Emoji:
	@staticmethod
	def emoji_to_8bit_escape(emoji):
		return emoji.encode('unicode-escape').decode('utf-8')


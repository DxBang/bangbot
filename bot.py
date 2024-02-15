import sys, traceback
from bang.bot import Bang

if __name__ == "__main__":
	try:
		bot = Bang()
		bot.run()
	except Exception as e:
		traceback.print_exc()
		sys.exit(1)


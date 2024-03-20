import os, sys
import traceback
import bang
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


if __name__ == "__main__":
	try:
		bot = bang.Bot(
			TOKEN
		)
		bot.run()
	except Exception as e:
		traceback.print_exc()
		sys.exit(1)

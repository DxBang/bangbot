import os, sys
import traceback
from bang.bot import Bang
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
with open('.version', 'r') as f:
	version = f.read().strip()

if __name__ == "__main__":
	try:
		bot = Bang(
			TOKEN,
			version
		)
		bot.run()
	except Exception as e:
		traceback.print_exc()
		sys.exit(1)

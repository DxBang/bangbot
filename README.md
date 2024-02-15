# Bang Bot
 Discord Bot

## Installation
1. Install Python 3.10 or higher
2. Setup the virtual environment using `python -m venv .venv`
3. Install the required packages using `pip install -r requirements.txt`
4. Create a `.env` file in the root directory and add the following:
```.env
DISCORD_TOKEN=<your_discord_bot_token>
```

## Configuration
The bot is configured using the `config.json` file. The file is structured as follows:
```json
{
  "prefix": [
	"!",
	"."
  ]
}
```
Enable the extensions by adding the file name to the `extensions` list in the `config.json` file. _(Hint: added ! before the extension name to indicate that it is disabled without removing it from the condig.)_

```json
{
  "extensions": [
	"bang.systems"
  ]
}
```

## Usage
Run the bot using (on Linux):
```shell
source .venv/bin/activate
python bot.py
deactivate
```

and on Windows:
```shell
.venv\Scripts\Activate.ps1
python bot.py
deactivate
```

## Features
Besides the basic (ping, welcome message etc.) features, the bot has the following features:

### Assetto Corsa Competizione @ G-Portal
`/result [date]` - Get the server status of the Assetto Corsa Competizione server hosted by G-Portal and generate a result image.



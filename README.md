# Bang Bot
_Discord Race Bot for Assetto Corsa Competizione_
![Race Bot](image/racebot-banner.png?raw=true "Race Bot")


![Danish eMotorsport Series](image/dems2024-logo-wht.png?raw=true "Danish eMotorsport Series")






## Installation
1. Install Python 3.10 or higher
2. Setup the virtual environment using `python -m venv .venv`
3. Activate the virtual enviroment using `source .venv/bin/activate` or `.venv\Scripts\Activate.ps1`
4. Install the required packages using `pip install -r requirements.txt`
5. Create a `.env` file in the root directory and add the following:
```.env
DISCORD_TOKEN=<your_discord_bot_token>
```

### Install on Linux as Service
1. Modified `bangbot.service` to match your installation.
2. cp `bangbot.service` to `/etc/systemd/system`
3. run `sudo systemctl daemon-reload`
4. run `sudo systemctl enable bangbot.service`
5. run `service bangbot restart`

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
		"bang.systems",
		"bang.acc-race",
		"bang.event"
	]
}
```

### Guild Configuration
Copy the `_default_.json` from `guild` and rename it to the guild id of the server. Modify the settings as you please.


## Usage
Run the bot using (on Linux):
```shell
source .venv/bin/activate
py bot.py
deactivate
```

and on Windows:
```shell
.venv\Scripts\Activate.ps1
py bot.py
deactivate
```

## Features
Besides the basic (ping, welcome message etc.) features, the bot has the following features:

### Assetto Corsa Competizione @ G-Portal or Nitrado.
`/practice [date]` - Get the practice results with the lap times and laps of the session.
`/qualify [date]` - Get the qualify results with the lap times and laps of the session.
`/race [date]` - Get the race results of the session and the final standings as well as the fastest lap and penalties.


### Event with Signup
```txt
/event Title of the event

Lots of text for the description of the event.
```
This will create an embed with 3 colums for Going, Maybe, & Decline where people can click on the reaction emojies to place their choice.

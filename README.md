# HTC Rule Bot
This bot provides a few commands for accessing the rules on HTC.
## Commands:
| Command | What does? |
| ------- | ---------- |
| `r.<rule id>` | Show the rule with a particular id. For example `r.A2` |
| `r.search <search term>` | Search the rules for a specific term |
| `r.die` | Shutdown the bot |
| `r.reload_rules` | Fetch the rules from Google Drive and update the local copy |
## Hosting:
### Requirements:
* `python 3.6`
* `discord.py 1.0.0a (rewrite)`
* `google-api-python-client`
### Files:
| File | What does? |
| ---- | ---------- |
| `./bot-token.txt` | Put your discord bot's token here. |
| `./client_secret.json` | This file is provided by Google (or me if you ask nicely), and allows the bot to authenticate with the Google API. |
| `./cache.txt` | This file is generated automatically by the bot. It contains a local copy of the rules document to save having to grab it every time. |
### Advice:
* Run the python file from a `while true; do ...; done` (or your terminal's equivalent) to facilitate the bot starting back up after a `r.die`.
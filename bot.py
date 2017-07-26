import httplib2
import os
import io

from googleapiclient.http import MediaIoBaseDownload
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import discord

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'HTC RuleBot'

PREFIX = 'r.'
TOKEN = open('bot-token.txt').read()

MAGICAL_POWERS = [161508165672763392, 140564059417346049, 312615171191341056, 149313154512322560,
                  154825973278310400, 185164223259607040, 127373929600778240, 184884413664854016,
                  164379304879194112,  98569889437990912, 184079890373541889,
]

SERVER_WHITELIST = [184755239952318464, 290573725366091787, 329367873858568210]


class RuleBot(discord.Client):
    def __init__(self):
        discord.Client.__init__(self)
        
        self.reload_cache()
        
        @self.event
        async def on_ready():
            print('RuleBot ready on {}'.format(self.user.name))
        
        @self.event
        async def on_message(message):
            if message.content.startswith(PREFIX):
                command = message.content[len(PREFIX):]
                
                if isinstance(message.channel, discord.abc.PrivateChannel) or message.guild.id in SERVER_WHITELIST:
                    if command == 'die':
                        if message.author.id in MAGICAL_POWERS:
                            await message.channel.send(':wave:')
                            await self.logout()
                    elif command.split(' ')[0] == 'help':
                        msg = '''```yaml
[ =-=-= RuleBot Help =-=-= ]
r.<rule id>             Show the rule with a particular id. For example r.A2
r.search <search term>  Search the rules for a specific term
r.help                  Show this help message
r.die                   Shutdown the bot
r.reload_rules          Fetch the rules from Google Drive and update the local copy
```For more information about the bot, view the GitHub page at <https://github.com/Bottersnike/HTCRuleBot>'''
                        await message.author.send(msg)
                        if not isinstance(message.channel, discord.abc.PrivateChannel):
                            await message.channel.send(':mailbox_with_mail:')
                    elif command.startswith('search '):
                        term = command[7:]
                        
                        found = []
                        
                        with message.channel.typing():
                            for block in self.rules:
                                for rule in self.rules[block]:
                                    if term.lower() in self.rules[block][rule].lower():
                                        found.append((block, rule, self.rules[block][rule]))
                        
                        if not found:
                            await message.channel.send('No rule found matching that term')
                        elif len(found) > 5:
                            await message.channel.send('I found too many results. Please refine your search.')
                        else:
                            m = 'I found:'
                            for f in found:
                                m += '\n**Rule {}{}:** {}'.format(*f)
                                
                                if len(m) > 1500:
                                    await message.channel.send(m)
                                    m = ''
                            if m:
                                await message.channel.send(m)
                    elif command == 'reload_rules':
                        if message.author.id in MAGICAL_POWERS:
                            with message.channel.typing():
                                self.reload_cache()
                            await message.channel.send('Done!')
                    else:
                        rule = self.lookup_rule(command)
                    
                        if rule is not None:
                            await message.channel.send('**Rule {}:** {}'.format(command.upper(), rule))
        
    def lookup_rule(self, code):
        if len(code) < 2:
            return None
        block = code[0].upper()
        num = code[1:]
        try:
            num = int(num)
        except ValueError:
            return None
        if block not in self.rules:
            return None
        
        block = self.rules[block]
        
        if num not in block:
            return None
        rule = block[num]
        
        return rule
    
    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'drive-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def parse_cache(self):
        with open('cache.txt', 'rb') as f:
            data = f.read().decode('utf-8')

        self.rules = {}
        rule_num = 1
        offense_block = None
        for line in data.split('\n'):
            if line.lower().startswith('code '):
                if offense_block != line[5].upper():
                    offense_block = line[5].upper()
                    rule_num = 1
                    self.rules[offense_block] = {}
            elif line.lower().startswith('notes'):
                break
            
            
            elif offense_block is not None:
                if line.startswith(' '):
                    self.rules[offense_block][rule_num - 1] += '\n' + line[3:]
                else:
                    num, rle = line.split(' ', 1)
                    num = num[:-1]
                    num = int(num)
                    
                    self.rules[offense_block][rule_num] = rle
                    rule_num += 1
        
    def reload_cache(self):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())

        service = discovery.build('drive', 'v3', http=http)
        
        request = service.files().export(fileId='137Fa99avZxFPovkiZRW7xSctFq2iirnKizZ4lHclHWU', mimeType='text/plain')
        data = request.execute()
        
        with open('cache.txt', 'wb') as f:
            f.write(data)
        
        self.parse_cache()

        
        
    def start_bot(self):
        self.run(TOKEN)


if __name__ == '__main__':
    b = RuleBot()
    b.start_bot()
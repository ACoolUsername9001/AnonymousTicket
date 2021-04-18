import discord
import json
import bidict
from discord.ext import commands


class AnonymousTicket(commands.Bot):

    def __init__(self, **options):
        super().__init__('!', **options)
        self.data = json.load(open('data.json'))
        self.ticket_channels = bidict.bidict()
        self.all_cogs = [
            'cogs.ticket'
        ]
        for extension in self.all_cogs:
            self.load_extension(extension)

    def set_data(self, gid: int, name: str, val):
        try:
            self.data[str(gid)].update({name: val})
        except KeyError:
            self.data.update({str(gid): {name: val}})
        json.dump(self.data, open('data.json', 'w'))

    def get_data(self, gid: int, name, default=None):
        try:
            return self.data[str(gid)][name]
        except KeyError:
            self.set_data(gid, name, default)
            return self.data[str(gid)][name]

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.channel in self.ticket_channels:
            await self.ticket_channels[message.channel].send(content=message.content)
        elif message.channel in self.ticket_channels.inv:
            await self.ticket_channels.inv[message.channel].send(content=message.author.mention + ': ' + message.content)

        await self.process_commands(message)

    async def on_ready(self):
        pass


if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False
    intents.bans = False
    intents.members = True

    bot = AnonymousTicket(intents=intents, max_messages=100)
    key = json.load(open('DiscordKey.json'))
    bot.run(key["key"])

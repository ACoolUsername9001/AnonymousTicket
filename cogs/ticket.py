import discord

from discord.ext import commands
from time import time

class Ticket(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def log_channel(self, channel: discord.TextChannel):
        pass

    @commands.command('ticket.open')
    async def ticket_open(self, ctx, *args):

        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.author.send("For your privacy the command you just typed is for my DMs only")
            await ctx.message.delete()
            return

        name = ' '.join(args)
        guilds = ctx.author.mutual_guilds
        guild = discord.utils.find(lambda g: g.name.lower() == name.lower(), guilds)
        ticket_role_ids = self.bot.get_data(guild.id, 'ticket_roles_ids', [])

        if not any(map(lambda r: r.id in ticket_role_ids, guild.get_member(ctx.author.id).roles)):
            await ctx.author.send("you do not have permissions to open a ticket in this guild")
            return

        category = discord.utils.get(guild.categories, id=self.bot.get_data(guild.id, 'ticket_category', 0))
        if not category:
            await ctx.author.send('This guild has not set up the ticket system yet')
            return

        ticket_channel = await category.create_text_channel('ticket-{}'.format(time()))
        self.bot.ticket_channels[ctx.channel] = ticket_channel

    @commands.command('ticket.close')
    async def ticket_close(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            if ctx.channel in self.bot.ticket_channels.keys():
                guild_channel = self.bot.ticket_channels[ctx.channel]
                self.log_channel(guild_channel)
                self.bot.ticket_channels.pop(ctx.channel)
                await guild_channel.delete()
            else:
                await ctx.send("I don't recall you opened a ticket")
        else:
            if ctx.channel not in self.bot.ticket_channels.inv:
                return
            self.log_channel(ctx.channel)
            self.bot.ticket_channels.inv.pop(ctx.channel)
            await ctx.channel.delete()


def setup(bot):
    bot.add_cog(Ticket(bot))

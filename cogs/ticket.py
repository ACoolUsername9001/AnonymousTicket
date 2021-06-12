import bidict
import discord

from discord.ext import commands
from time import time


def dms_only():
    def predicate(ctx: commands.Context):
        return isinstance(ctx.channel, discord.DMChannel)
    return commands.check(predicate)


def is_ticket_open(ctx: commands.Context, ticket_channels):
    return ctx.channel in ticket_channels or ctx.channel in ticket_channels.inverse


class Ticket(commands.Cog):

    def __init__(self, bot):
        self.ticket_channels: bidict.BidictBase[discord.abc.Messageable, discord.abc.Messageable] = bidict.bidict()
        self.bot = bot

    # def log_channel(self, channel: discord.TextChannel):
    #     pass

    @commands.Cog.listener('on_message')
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.channel in self.ticket_channels:

            try:
                await self.ticket_channels[message.channel].send(content=message.content)
                if message.attachments:
                    await self.ticket_channels[message.channel].send('\n'.join([a.url for a in message.attachments]))
            except Exception as e:
                await message.channel.send("Could not send message, reason: {}".format(e))

        elif message.channel in self.ticket_channels.inverse:
            try:
                await self.ticket_channels.inverse[message.channel].send(content=message.author.mention + ': ' + message.content)
                await self.ticket_channels.inverse[message.channel].send('\n'.join([a.url for a in message.attachments]))
            except Exception as e:
                await message.channel.send("Could not send message, reason: {}".format(e))

    @commands.command('ticket.open')
    async def ticket_open(self, ctx, *args):

        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.author.send("For your privacy the command you just typed is for my DMs only")
            await ctx.message.delete()
            return

        if ctx.channel in self.ticket_channels:
            await ctx.send("You have already opened a ticket, please close it using `!ticket.close` to open a new one")
            return

        name = ' '.join(args)
        guilds = ctx.author.mutual_guilds
        guild = discord.utils.find(lambda g: g.name.lower() == name.lower(), guilds)
        if guild is None:
            await ctx.send("I Don't know that guild")
            return

        ticket_role_ids = self.bot.get_data(guild.id, 'ticket_roles_ids', [])

        if not any(map(lambda r: r.id in ticket_role_ids, guild.get_member(ctx.author.id).roles)):
            await ctx.author.send("you do not have permissions to open a ticket in this guild")
            return

        category = discord.utils.get(guild.categories, id=self.bot.get_data(guild.id, 'ticket_category', 0))
        if not category:
            await ctx.author.send('This guild has not set up the ticket system yet')
            return

        ticket_channel = await category.create_text_channel('ticket-{}'.format(time()))
        self.ticket_channels[ctx.channel] = ticket_channel
        await ctx.send("The ticket is now open, talk to me and I'll pass it on")

    @commands.command('ticket.close')
    async def ticket_close(self, ctx):
        if not is_ticket_open(ctx, self.ticket_channels):
            await ctx.send("there is no open ticket linked to this channel")
            return

        if isinstance(ctx.channel, discord.DMChannel):
            if ctx.channel in self.ticket_channels.keys():
                guild_channel = self.ticket_channels[ctx.channel]
                # self.log_channel(guild_channel)
                self.ticket_channels.pop(ctx.channel)
                await ctx.channel.send("Ticket closed, I will no longer pass your messages to the server")
                # await guild_channel.delete()
        else:
            if ctx.channel not in self.ticket_channels.inverse:
                return
            # self.log_channel(ctx.channel)
            dm_channel = self.ticket_channels.inverse.pop(ctx.channel)
            await dm_channel.send("Ticket closed, I will no longer pass your messages to the server")
            # await ctx.channel.delete()

    @commands.command('ticket.exclude')
    async def ticket_exclude(self, ctx, members: commands.Greedy[discord.Member]):
        if not is_ticket_open(ctx, self.ticket_channels):
            await ctx.send("there is no open ticket linked to this channel")
            return

        if isinstance(ctx.channel, discord.DMChannel):
            ticket_channel = self.ticket_channels[ctx.channel]
        else:
            ticket_channel = ctx.channel

        if isinstance(ticket_channel, discord.TextChannel):
            exclude_permission = discord.PermissionOverwrite(view_channel=False)
            for member in members:
                await ticket_channel.set_permissions(member, overwrite=exclude_permission)

    @commands.command('ticket.include')
    async def ticket_include(self, ctx, members: commands.Greedy[discord.Member]):
        if not is_ticket_open(ctx, self.ticket_channels):
            await ctx.send("there is no open ticket linked to this channel")
            return

        if isinstance(ctx.channel, discord.DMChannel):
            ticket_channel = self.ticket_channels[ctx.channel]
        else:
            ticket_channel = ctx.channel

        if isinstance(ticket_channel, discord.TextChannel):
            include_permission = discord.PermissionOverwrite(view_channel=True)
            for member in members:
                await ticket_channel.set_permissions(member, overwrite=include_permission)


def setup(bot):
    bot.add_cog(Ticket(bot))

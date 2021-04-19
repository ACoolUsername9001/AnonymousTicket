import discord

from discord.ext import commands
from time import time


def dms_only():
    def predicate(ctx: commands.Context):
        return isinstance(ctx.channel, discord.DMChannel)
    return commands.check(predicate)


def open_ticket_check():
    def predicate(ctx: commands.Context):
        return ctx.channel in ctx.bot.ticket_channels or ctx.channel in ctx.bot.ticket_channels.inv
    return commands.check(predicate)


class Ticket(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # def log_channel(self, channel: discord.TextChannel):
    #     pass

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
    @open_ticket_check()
    async def ticket_close(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            if ctx.channel in self.bot.ticket_channels.keys():
                guild_channel = self.bot.ticket_channels[ctx.channel]
                # self.log_channel(guild_channel)
                self.bot.ticket_channels.pop(ctx.channel)
                await ctx.channel.send("Ticket closed")
                # await guild_channel.delete()
        else:
            if ctx.channel not in self.bot.ticket_channels.inv:
                return
            # self.log_channel(ctx.channel)
            dm_channel = self.bot.ticket_channels.inv.pop(ctx.channel)
            await dm_channel.send("Ticket closed")
            # await ctx.channel.delete()

    @commands.command('ticket.exclude')
    @open_ticket_check()
    async def ticket_exclude(self, ctx, members: commands.Greedy[discord.Member]):
        if isinstance(ctx.channel, discord.DMChannel):
            ticket_channel = self.bot.ticket_channels[ctx.channel]
        else:
            ticket_channel = ctx.channel

        if isinstance(ticket_channel, discord.TextChannel):
            exclude_permission = discord.PermissionOverwrite(view_channel=False)
            for member in members:
                await ticket_channel.set_permissions(member, overwrite=exclude_permission)

    @commands.command('ticket.include')
    @open_ticket_check()
    async def ticket_include(self, ctx, members: commands.Greedy[discord.Member]):
        if isinstance(ctx.channel, discord.DMChannel):
            ticket_channel = self.bot.ticket_channels[ctx.channel]
        else:
            ticket_channel = ctx.channel

        if isinstance(ticket_channel, discord.TextChannel):
            include_permission = discord.PermissionOverwrite(view_channel=True)
            for member in members:
                await ticket_channel.set_permissions(member, overwrite=include_permission)


def setup(bot):
    bot.add_cog(Ticket(bot))

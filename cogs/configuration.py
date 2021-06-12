import discord

from discord.ext import commands


class Configuration(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        return (not isinstance(ctx.channel, discord.DMChannel)) and (ctx.author.guild_permissions.administrator or (self.bot.get_data(ctx.guild.id, 'configurator_role', 0) in ctx.author.roles))

    @commands.guild_only()
    @commands.command('config.category.set')
    async def set_category(self, ctx, category: discord.CategoryChannel):
        if category not in ctx.guild.channels:
            await ctx.send("I can't find this category on the server")
            return

        self.bot.set_data(ctx.guild.id, 'ticket_category', category.id)
        await ctx.send("Category \"{}\" has been set as the ticket category".format(category.name))

    @commands.command('config.configurator.set')
    @commands.guild_only()
    async def set_configurator_role(self, ctx, role: discord.Role):
        if role not in ctx.guild.roles:
            await ctx.send("I can't find this role on this server")
            return
        self.bot.set_data(ctx.guild.id, 'configurator_role', role.id)
        await ctx.send("Role \"{}\" has been set as the configurator role".format(role.mention))

    @commands.command('config.category.get')
    @commands.guild_only()
    async def get_category(self, ctx):
        category_id = self.bot.get_data(ctx.guild.id, 'ticket_category')
        if category_id:
            category = discord.utils.get(ctx.guild.channels, id=category_id)

            embed = discord.Embed(color=discord.Color.random())
            embed.title = 'Category'
            embed.add_field(name='Category Name', value=category.name)
            embed.add_field(name='Category ID', value=category.id)
            await ctx.send(embed=embed)
        else:
            await ctx.send("There is no ticket category yet, add one using `!config.set.category`")

    @commands.command('config.configurator.get')
    @commands.guild_only()
    async def get_configurator(self, ctx):
        role_id = self.bot.get_data(ctx.guild.id, 'configurator_role', None)
        if role_id is not None:
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            embed = discord.Embed(color=discord.Color.random())
            embed.title = 'Configurator'
            embed.description = role.mention
            await ctx.send(embed=embed)
        else:
            await ctx.send("There is no configurator role yet, add one using `!config.set.configurator`")

    @commands.command('config.ticket-roles.get')
    @commands.guild_only()
    async def get_ticket_roles(self, ctx):
        role_ids = self.bot.get_data(ctx.guild.id, 'ticket_roles_ids', [])
        if role_ids:
            roles = [role.mention for role in ctx.guild.roles if role.id in role_ids]
            embed = discord.Embed(color=discord.Color.random())
            embed.title = 'Ticket Roles'
            embed.description = ' '.join(roles)
            await ctx.send(embed=embed)
        else:
            await ctx.send("There are no ticket roles yet, add some using `!config.add.ticket_role`")

    @commands.command('config.ticket-roles.remove')
    @commands.guild_only()
    async def remove_ticket_roles(self, ctx, roles_to_remove: commands.Greedy[discord.Role]):
        roles = self.bot.get_data(ctx.guild.id, 'ticket_roles_ids', [])
        for r in roles_to_remove:
            roles.remove(r.id)
        self.bot.set_data(ctx.guild.id, 'ticket_roles_ids', roles)
        await ctx.send("Roles \"{}\" can no longer open a ticket".format(' '.join(r.mention for r in roles_to_remove)))

    @commands.command('config.ticket-roles.add')
    @commands.guild_only()
    async def add_ticket_roles(self, ctx, roles_to_add: commands.Greedy[discord.Role]):
        roles_to_add = [role for role in roles_to_add if role in ctx.guild.roles]

        roles = self.bot.get_data(ctx.guild.id, 'ticket_roles_ids', [])
        roles.extend((r.id for r in roles_to_add))

        self.bot.set_data(ctx.guild.id, 'ticket_roles_ids', roles)
        await ctx.send("Roles \"{}\" can now open a ticket".format(' '.join(role.mention for role in roles_to_add)))


def setup(bot):
    bot.add_cog(Configuration(bot))

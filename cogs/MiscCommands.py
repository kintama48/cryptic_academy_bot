from random import randint

import discord
from discord.ext import commands
import json
import os
import sys

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


#
# with open('invites.json', 'r') as o:
#     invite_uses = json.load(o)

def has_roles(context):
    roles = [role.name for role in context.message.author.roles]
    if "Admin" in roles:
        return True
    return False


def update_config():
    with open('config.json', 'w') as fp:
        json.dump(config, fp)


prefix = config["bot_prefix"]


class MiscCommands(commands.Cog, name="misc"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="currency",
                      description=f"Shows the list of all available currencies. Syntax: '<prefix>currency'")
    async def currency(self, context):
        embed = discord.Embed(color=randint(0, 0xffff), description="**Available Currencies**\n"
                                                                    "**     1. $USD**\n"
                                                                    "**     2. ₱PHP**\n")
        await context.reply(embed=embed)

    @commands.command(name="ping",
                      description=f"Checks the Latency of the bot. Syntax: '<prefix>ping'")
    async def ping(self, context):
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0xD5059D
        )
        await context.reply(embed=embed)

    @commands.command(name="quote", description=f"Quotes what the user said. Syntax: '<prefix>quote <message>'")
    async def quote(self, context, *, args):
        if has_roles(context):
            embed = discord.Embed(
                description=args,
                color=0x42F56C
            )
            await context.reply(content=f"{context.author.mention} said: ", embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, (commands.CommandNotFound, discord.HTTPException)):
            return

        if isinstance(error, commands.MissingPermissions):
            return await ctx.send(embed=discord.Embed(
                title="Error",
                description="You don't have the permission to use this command."))
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=discord.Embed(
                title="Error",
                description=f"You forgot to provide an argument, please do it like: `{ctx.command.name} {ctx.command.usage}`"))


def setup(bot):
    bot.add_cog(MiscCommands(bot))

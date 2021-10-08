import json
import os
import sys
from random import randint

import discord
from discord.ext import commands

from utils.axie_cards import card_finder

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

prefix = config['bot_prefix']



def has_roles(context):
    roles = [role.name for role in context.message.author.roles]
    if "Admin" in roles:
        return True
    return False

class Info(commands.Cog, name="info"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="attackorder",
                      description=f"Info about attack order.")
    async def attackorder(self, context):
        await context.reply(content=context.message.author.mention,
                           embed=discord.Embed(color=randint(0, 0xffff), description="**Higher Speed** > **Lower HP** > "
                                                                              "**Higher Skill** > **Higher Morale** >"
                                                                              " **Lower Fighter ID**"))

    @commands.command(name="card",
                      description=f"Shows the information of the specified card. Syntax: '<prefix>card <part name | skill name'")
    async def card(self, context, *args):
        part_or_skill_name = " ".join(args)
        img = card_finder(part_or_skill_name)
        if img:
            file = discord.File(fp=img)
            await context.reply(content=context.author.mention, file=file)
            return
        await context.reply(content=context.author.mention, embed=discord.Embed(color=0xffff, description=f'*Failed to find the`{part_or_skill_name}` card.*'))

    @commands.command(name="buffs",
                      description=f"Info about buffs (Icon, Name, Description)")
    async def buffs(self, context):
        embed = discord.Embed(color=randint(0, 0xffff), description="**Buffs**")
        embed.add_field(name=":attackup: **Attack Up**", value="Increases the next Attack by 20%.", inline=False)
        embed.add_field(name=":moraleup: **Morale Up**", value="Increases Morale by 20% for the next round.", inline=False)
        embed.add_field(name=":speedup: **Speed Up**", value="Increases Speed by 20% for the next round.", inline=False)
        await context.reply(content=context.message.author.mention, embed=embed)

    @commands.command(name="debuffs",
                      description=f"Info about debuffs (Icon, Name, Description)")
    async def debuffs(self, context):
        embed = discord.Embed(color=randint(0, 0xffff), description="**Debuffs**")
        embed.add_field(name=":aroma: **Aroma**", value="Target priority changes to affected Axie for the next round.", inline=False)
        embed.add_field(name=":attackdown: **Attack Down**", value="Decreases the next Attack by 20%.", inline=False)
        embed.add_field(name=":chill: **Chill**", value="Affected Axie can't enter last stand.", inline=False)
        embed.add_field(name=":fear: **Fear**", value="Affected Axie attack.", inline=False)
        embed.add_field(name=":fragile: **Fragile**", value="Shield takes double the damage for the next incoming attack.", inline=False)
        embed.add_field(name=":jinx: **Jinx**", value="Affected Axie can't land critcal hits for the next round.", inline=False)
        embed.add_field(name=":lethal: **Lethal**", value="Next hit against affected Axie is critical.", inline=False)
        embed.add_field(name=":moraledown: **Morale Down**", value="Decreases Morale by 20% for the next round.", inline=False)
        embed.add_field(name=":sleep: **Sleep**", value="Next incoming attack ignores shields.", inline=False)
        embed.add_field(name=":speeddown: **Speed Down**", value="Decreases Speed by 20% for the next round.", inline=False)
        embed.add_field(name=":stench: **Stench**", value="	Affected Axie loses target priority for the next round.", inline=False)
        embed.add_field(name=":stun: **Stun**", value="Next attack misses / Next incoming attack ignores shields.", inline=False)
        await context.reply(content=context.message.author.mention, embed=embed)

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
    bot.add_cog(Info(bot))

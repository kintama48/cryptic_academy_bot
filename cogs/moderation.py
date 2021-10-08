import discord
from discord.ext import commands
import json
import os
import sys

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

prefix = config['bot_prefix']


def has_roles(context):
    roles = [role.id for role in context.message.author.roles]
    if 868328584916385812 in roles:
        return True
    return False


class ModerationCog(commands.Cog, name="moderation"):
    def __init__(self, bot):
        self.bot = bot

    # kick out a user from the server
    @commands.command(name='kick', pass_context=True, description="Kick out a user")
    async def kick(self, context, member: discord.Member, *, reason="Not specified"):
        if has_roles(context):
            if member.guild_permissions.administrator:
                embed = discord.Embed(
                    title="Error!",
                    description="User has Admin permissions.",
                    color=0x541760
                )
                await context.send(embed=embed)
            else:
                try:
                    await member.kick(reason=reason)
                    embed = discord.Embed(
                        title="User Kicked!",
                        description=f"**{member}** was kicked by **{context.message.author}**!",
                        color=0x42F56C
                    )
                    embed.add_field(
                        name="Reason:",
                        value=reason
                    )
                    await context.send(embed=embed)
                    try:
                        await member.send(
                            f"You were kicked by **{context.message.author}**!\nReason: {reason}"
                        )
                    except:
                        pass
                except:
                    embed = discord.Embed(
                        title="Error!",
                        description="An error occurred while trying to kick the user. Make sure my role is above the role "
                                    "of the user you want to kick.",
                        color=0x541760
                    )
                    await context.message.channel.send(embed=embed)

    # change the nickname of a user
    @commands.command(name="nickname", description="Change the nickname of a user")
    async def nickname(self, context, member: discord.Member, *, nickname=None):
        if has_roles(context):
            try:
                await member.edit(nick=nickname)
                embed = discord.Embed(
                    title="Changed Nickname!",
                    description=f"**{member}'s** new nickname is **{nickname}**!",
                    color=0x42F56C
                )
                await context.send(embed=embed)
            except:
                embed = discord.Embed(
                    title="Error!",
                    description="An error occurred while trying to change the nickname of the user. Make sure my role is "
                                "above the role of the user you want to change the nickname.",
                    color=0x541760
                )
                await context.message.channel.send(embed=embed)

    # ban a user
    @commands.command(name="ban", description="Ban a user")
    async def ban(self, context, member: discord.Member, *, reason="Not specified"):
        if has_roles(context):
            try:
                if member.guild_permissions.administrator:
                    embed = discord.Embed(
                        title="Error!",
                        description="User has Admin permissions.",
                        color=0x541760
                    )
                    await context.send(embed=embed)
                else:
                    await member.ban(reason=reason)
                    embed = discord.Embed(
                        title="User Banned!",
                        description=f"**{member}** was banned by **{context.message.author}**!",
                        color=0x42F56C
                    )
                    embed.add_field(
                        name="Reason:",
                        value=reason
                    )
                    await context.send(embed=embed)
                    await member.send(f"You were banned by **{context.message.author}**!\nReason: {reason}")
            except:
                embed = discord.Embed(
                    title="Error!",
                    description="An error occurred while trying to ban the user. Make sure my role is above the role of "
                                "the user you want to ban.",
                    color=0x541760
                )
                await context.send(embed=embed)

    # warn a user in their DMs
    @commands.command(name="warn",
                      description="Warn a user in their DMs. Has an extra reason argument followed by the member's @.")
    async def warn(self, context, member: discord.Member, *, reason="Not specified"):
        if has_roles(context):
            embed = discord.Embed(
                title="User Warned!",
                description=f"**{member}** was warned by **{context.message.author}**!",
                color=0x42F56C
            )
            embed.add_field(
                name="Reason:",
                value=reason
            )
            await context.send(embed=embed)
            try:
                await member.send(f"You were warned by **{context.message.author}**!\nReason: {reason}")
            except:
                pass

    # delete an n number of messages
    @commands.command(name="purge", description="Deletes an n number of messages")
    async def purge(self, context, amount):
        if has_roles(context):
            channel = context.message.channel
            try:
                amount = int(amount) + 1
            except:
                embed = discord.Embed(
                    title="Error!",
                    description=f"`{amount}` is not a valid number.",
                    color=0x541760
                )
                await context.send(embed=embed)
                return
            if amount < 1:
                embed = discord.Embed(
                    title="Error!",
                    description=f"`{amount}` is not a valid number.",
                    color=0x541760
                )
                await context.send(embed=embed)
                return
            purged_messages = await channel.purge(limit=amount)
            embed = discord.Embed(
                title="Chat Cleared!",
                description=f"**{context.message.author}** cleared **{len(purged_messages) - 1}** messages!",
                color=0x541760
            )
            await context.send(embed=embed)

    # dm's a user
    @commands.command(name="dm", description="DMs a user. Syntax: <prefix>dm [member @] [message]")
    async def dm(self, context, member: discord.Member, *, message):
        if has_roles(context):
            embed = discord.Embed(
                description=f"{message}",
                color=0xD5059D
            )
            try:
                # To know what permissions to give to your bot, please see here: https://discordapi.com/permissions.html and remember to not give Administrator permissions.
                await member.send(embed=embed)
                await context.send(f"I sent {member.display_name} a private message!")
            except discord.Forbidden:
                await context.send(embed=embed)

    @commands.command(name="serverinfo", description="Display the server's info")
    async def serverinfo(self, context):
        server = context.message.guild
        roles = [x.name for x in server.roles]
        roles.pop(0)
        role_length = len(roles)
        if role_length > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
        roles = ", ".join(roles)
        channels = len(server.channels)
        time = str(server.created_at)
        time = time.split(" ")
        time = time[0]

        embed = discord.Embed(
            title="**Server Name:**",
            description=f"{server}",
            color=0x42F56C
        )
        embed.set_thumbnail(
            url=server.icon_url
        )
        embed.add_field(
            name="Owner:",
            value="jeraldlanchinebre#0021"
        )
        embed.add_field(
            name="Server ID:",
            value=server.id
        )
        embed.add_field(
            name="Member Count:",
            value=server.member_count
        )
        embed.add_field(
            name="Text/Voice Channels:",
            value=f"{channels}"
        )
        embed.add_field(
            name=f"Roles ({role_length}):",
            value=roles
        )
        embed.set_footer(
            text=f"Created at: {time}"
        )
        await context.send(embed=embed)

    @commands.command(name="setprefix",
                      description=f"Sets the specified prefix for the server. Syntax: '<prefix>setprefix <prefix>'")
    async def setprefix(self, context, prefix):
        if has_roles(context):
            config['bot_prefix'] = prefix
            with open('config.json') as file:
                json.dump(config, file)
            return

    @commands.command(name="setcurrency",
                      description=f"Sets the specified currency for the server. Syntax: '<prefix>setcurrency <currency>'")
    async def setcurrency(self, context, currency):
        if has_roles(context):
            config['currency'] = currency
            with open('config.json') as file:
                json.dump(config, file)
            return

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
    bot.add_cog(ModerationCog(bot))

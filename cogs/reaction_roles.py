import discord
import custom_checks
from discord.ext import commands
from config import discordClient, DB_conn, cur


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True, aliases=["reactionroles", "reaction roles",])
    async def rr(self, ctx):
        await ctx.send("reaction roles")

    @rr.command()
    @custom_checks.allowed_roles("poll_role", "poll_channel")
    async def add(self, ctx, emoji, message_id, role_id, channel_id=None):
        if len(emoji) != 1:
            emoji_id = emoji[-19:-1]
        else:
            emoji_id = emoji

        if channel_id is None:
            channel_id = ctx.channel.id

        if len(emoji_id) != 1 and (len(emoji_id) != 18 or not emoji_id.isdigit()):
            if len(message_id) != 18 or not message_id.isdigit():
                if len(role_id) != 18 or not role_id.isdigit():
                    if len(channel_id) != 18 or not channel_id.isdigit():
                        await ctx.send("Make sure to follow the format `w!rr add <emoji> <message_id> <role_id> [channel_id]")
                        return

        sql = f"INSERT INTO reaction_roles (message_id , emoji_id, guild_id, role_id, channel_id) " \
              f"VALUES ('{message_id}', '{emoji_id}', '{ctx.guild.id}', '{role_id}', '{channel_id}')"

        try:
            channel = await discordClient.fetch_channel(channel_id)
            try:
                message = await channel.fetch_message(message_id)
                try:
                    await message.add_reaction(emoji)
                    cur.execute(sql, ())
                    DB_conn.commit()
                except discord.Forbidden:
                    await ctx.send("I Dont Have Permission To Add Reactions Here")
                except discord.NotFound:
                    await ctx.send("I Could Not Find That Emoji")
            except discord.NotFound:
                await ctx.send(
                    "I Couldnt Find That Message. Make Sure The Message Is In This Channel And It Is A Valid Message ID: `w!rr id`\n"
                    "If The Message Is Not In This Channel Add The Channel ID After The Role ID In The Command.")
        except discord.NotFound:
            await ctx.send("I Couldent Find The Channel You Wanted")

    @rr.command()
    async def remove(self, ctx, emoji, message_id):
        if len(emoji) != 1 and (len(emoji) != 18 or emoji.isdigit()):
            if len(message_id) != 18 or message_id.isdigit():
                await ctx.send("Make sure to follow the format `w!rr remove <emoji> <message_id>")
                return
        sql = f"DELETE FROM reaction_roles " \
            f"WHERE message_id='{message_id}' AND emoji_id='{emoji}'"
        cur.execute(sql, ())
        if cur.rowcount == 0:
            await ctx.send("That Is Not A Reaction Role Message/Emoji")
        else:
            DB_conn.commit()
            await ctx.send("Successfully Deleted The Reaction Role")

    @rr.command()
    async def id(self, ctx):
        await ctx.message.delete()
        image = discord.File("images/discord_id.jpg")
        await ctx.send(file=image)

    @rr.command(aliases=["show", ])
    async def list(self, ctx):
        await ctx.message.delete()
        sql = f"SELECT emoji_id, message_id, role_id, channel_id FROM reaction_roles " \
            f"WHERE guild_id='{ctx.guild.id}'"
        cur.execute(sql, ())
        rr_list = cur.fetchall()
        rr_string = ""
        for row in rr_list:
            if len(row[0]) == 18:
                emoji = await ctx.guild.fetch_emoji(int(row[0]))
                emoji = f"<:{emoji.name}:{row[0]}>"
            else:
                emoji = row[0]

            role = ctx.guild.get_role(int(row[2]))
            if role is None:
                role = "Not Found"
            else:
                role = role.mention
            rr_string = f"{rr_string}» [Message](https://discordapp.com/channels/{ctx.guild.id}/{row[3]}/{row[1]}) | Emoji : {emoji} | Role: {role}\n"
        embed = discord.Embed(title=f"{ctx.guild.name}'s Reaction Roles",
                              description=rr_string,
                              type="rich",)
        await ctx.send(embed=embed)

    @commands.Cog.listener('on_raw_reaction_add')
    async def reaction_add_listener(self, payload):
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = payload.emoji
        sql = f"SELECT role_id " \
            f"FROM reaction_roles " \
            f"WHERE message_id='{payload.message_id}' and emoji_id='{emoji}'"
        cur.execute(sql, ())
        role = cur.fetchone()
        if role is not None:
            try:
                await payload.member.add_roles(discord.Object(int(role[0])), reason="Reaction Roles")
            except discord.Forbidden:
                try:
                    await payload.send(f"I Dont Have permission To Add Roles To {payload.member.name}")
                except discord.Forbidden:
                    pass

    @commands.Cog.listener('on_raw_reaction_remove')
    async def reaction_remove_listener(self, payload):
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = payload.emoji

        sql = f"SELECT role_id " \
            f"FROM reaction_roles " \
            f"WHERE message_id='{payload.message_id}' and emoji_id='{emoji}'"
        cur.execute(sql, ())
        role = cur.fetchone()
        if role is not None:
            guild = discordClient.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            try:
                await member.remove_roles(discord.Object(int(role[0])), reason="Reaction Roles")
            except discord.Forbidden:
                try:
                    await payload.send(f"I Dont Have permission To Remove Roles From {payload.member.name}")
                except discord.Forbidden:
                    pass


def setup(client):
    client.add_cog(ReactionRoles(client))

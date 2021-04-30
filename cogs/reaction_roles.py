import discord
import custom_checks
import global_functions
from discord.ext import commands
from config import discordClient


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True, aliases=["reactionroles", "reaction roles",], )
    @custom_checks.allowed_roles("rr_role", "rr_channel")
    async def rr(self, ctx, emoji):
        print(emoji)
        await ctx.send("reaction roles")

    @rr.command()
    @custom_checks.allowed_roles("rr_role", "rr_channel")
    async def add(self, ctx, emoji, message_id, role_id, channel_id=None):
        # if len(emoji) != 1:
        #     emoji_id = emoji[-19:-1]
        # else:
        #     emoji_id = emoji

        try:
            emoji_id = await commands.PartialEmojiConverter().convert(ctx=ctx, argument=emoji)
            emoji_id = emoji_id.id
        except commands.BadArgument:
            emoji_id = emoji

        if channel_id is None:
            channel_id = ctx.channel.id

        # if len(emoji_id) != 1 and (len(emoji_id) != 18 or not emoji_id.isdigit()):
        if len(message_id) != 18 or not message_id.isdigit():
            if len(role_id) != 18 or not role_id.isdigit():
                if channel_id is not None:
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
                    await self.bot.db.execute(sql, ())
                    await self.bot.db.commit()
                    await ctx.send("The Reaction Role Was Added!")
                except discord.Forbidden:
                    await ctx.send("I Dont Have Permission To Add Reactions Here")
                except discord.HTTPException:
                    await ctx.send("I Could Not Find That Emoji")
            except discord.NotFound:
                await ctx.send(
                    "I Couldnt Find That Message. Make Sure The Message Is In This Channel And It Is A Valid Message ID: `w!rr id`\n"
                    "If The Message Is Not In This Channel Add The Channel ID After The Role ID In The Command.")
        except discord.NotFound:
            await ctx.send("I Couldent Find The Channel You Wanted")

    @rr.command()
    @custom_checks.allowed_roles("rr_role", "rr_channel")
    async def remove(self, ctx, emoji, message_id):
        # if len(emoji) != 1 and (len(emoji) != 18 or emoji.isdigit()):
        if len(message_id) != 18 or not message_id.isdigit():
            await ctx.send("Make sure to follow the format `w!rr remove <emoji> <message_id>")
            return

        try:
            emoji_id = await commands.PartialEmojiConverter().convert(ctx=ctx, argument=emoji)
            emoji_id = emoji_id.id
        except commands.BadArgument:
            emoji_id = emoji

        sql = f"DELETE FROM reaction_roles " \
            f"WHERE message_id='{message_id}' AND emoji_id='{emoji_id}'"

        try:
            await ctx.message.add_reaction(emoji)
            await self.bot.db.execute(sql, ())

            if await self.bot.db.rowcount == 0:
                await ctx.send("That Is Not A Reaction Role Message/Emoji")
            else:
                await self.bot.db.commit()
                await ctx.send("Successfully Deleted The Reaction Role")
        except discord.HTTPException:
            await ctx.send("That Is Not A Valid Emoji")

    @rr.command()
    @custom_checks.allowed_roles("rr_role", "rr_channel")
    async def id(self, ctx):
        await ctx.message.delete()
        image = discord.File("images/discord_id.jpg")
        await ctx.send(file=image)

    @rr.command(aliases=["show", ])
    @custom_checks.allowed_roles("rr_role", "rr_channel")
    async def list(self, ctx):
        await ctx.message.delete()
        sql = f"SELECT emoji_id, message_id, role_id, channel_id FROM reaction_roles " \
            f"WHERE guild_id='{ctx.guild.id}'"
        await self.bot.db.execute(sql, ())
        rr_list = await self.bot.db.fetchall()
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
        await self.bot.db.execute(sql, ())
        role = await self.bot.db.fetchone()
        if role is not None:
            try:
                await payload.member.add_roles(discord.Object(int(role[0])), reason="Reaction Roles")
            except discord.Forbidden:
                try:
                    await payload.channel.send(f"I Dont Have permission To Add Roles To {payload.member.name}")
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
        await self.bot.db.execute(sql, ())
        role = await self.bot.db.fetchone()
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

    @rr.error
    @add.error
    @remove.error
    @id.error
    @list.error
    async def rr_error(self, ctx, error):
        print(f"RR Error: {error}")
        await ctx.message.delete()
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=await global_functions.create_embed(title="fail",
                                                                     description=
                                                                     "You Do Not Have Permission To Preform That Command"))


def setup(client):
    client.add_cog(ReactionRoles(client))

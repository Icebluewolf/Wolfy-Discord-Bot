import discord
import custom_checks
import global_functions
from discord.ext import commands
from config import discordClient
from discord.commands import SlashCommandGroup, Option


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    rr = SlashCommandGroup("reactionroles", "To Handle The Reaction Role Commands. But Probably Not Useful Now")

    # @custom_checks.has_perms("rr")
    # async def rr(self, ctx):
    #     await ctx.respond("reaction roles")

    @rr.command(description="Add A Reaction That Is Linked To A Role To A Message")
    @custom_checks.has_perms("rr")
    async def add(self, ctx,
                  emoji: Option(str, description="The Emoji To Use In The Reaction"),
                  message_id: Option(str, description="The ID Of The Message To Add The Reaction To"),
                  role_id: Option(discord.Role, description="The Role To Link With The Reaction"),
                  channel_id: Option(discord.TextChannel,
                                     description="If The Message Is Not In This Channel Give The Channel ID",
                                     required=False)):

        if not message_id.isnumeric():
            return await ctx.respond("Your Message Id Is Invalid. See `/reactionroles id`")

        try:
            emoji_id = await commands.PartialEmojiConverter().convert(ctx=ctx, argument=emoji)
            emoji_id = emoji_id.id
        except commands.BadArgument:
            emoji_id = emoji

        if channel_id is None:
            channel_id = ctx.channel.id

        sql = f"INSERT INTO reaction_roles (message_id , emoji_id, guild_id, role_id, channel_id) " \
              f"VALUES ($1, $2, $3, $4, $5)"

        try:
            channel = await discordClient.fetch_channel(channel_id)
            try:
                message = await channel.fetch_message(message_id)
                try:
                    await message.add_reaction(emoji)
                    await self.bot.db.execute(sql, message_id, emoji_id, ctx.guild.id, role_id, channel_id)
                    await ctx.respond("The Reaction Role Was Added!")
                except discord.Forbidden:
                    await ctx.respond("I Dont Have Permission To Add Reactions Here")
                except discord.HTTPException:
                    await ctx.respond("I Could Not Find That Emoji")
            except discord.NotFound:
                await ctx.respond(
                    "I Could Not Find That Message. Make Sure The Message Is In This Channel And It Is A Valid Message "
                    "ID: `/rr id`\n"
                    "If The Message Is Not In This Channel Add The Channel ID After The Role ID In The Command.")
        except discord.NotFound:
            await ctx.respond("I Could Not Find The Channel You Wanted")

    @rr.command(description="Removes A Reaction Role From A Message")
    @custom_checks.has_perms("rr")
    async def remove(self, ctx,
                     emoji: Option(str, description="The Emoji Of The Reaction Role To Be Removed"),
                     message_id: Option(str, description="The ID Of The Message To Remove The Reaction From")):

        if not message_id.isnumeric():
            return await ctx.respond("Your Message Id Is Invalid. See `/reactionroles id`")

        try:
            emoji_id = await commands.PartialEmojiConverter().convert(ctx=ctx, argument=emoji)
            emoji_id = emoji_id.id
        except commands.BadArgument:
            emoji_id = emoji

        sql = f"DELETE FROM reaction_roles " \
            f"WHERE message_id=$1 AND emoji_id=$2"

        try:
            await ctx.message.add_reaction(emoji)
            await self.bot.db.execute(sql, message_id, emoji_id)

            if await self.bot.db.rowcount == 0:
                await ctx.respond("That Is Not A Reaction Role Message/Emoji")
            else:
                await ctx.respond("Successfully Deleted The Reaction Role")
        except discord.HTTPException:
            await ctx.respond("That Is Not A Valid Emoji")

    @rr.command(description="Shows An Image Of How To Get A Discord ID")
    @custom_checks.has_perms("rr")
    async def id(self, ctx):
        image = discord.File("images/discord_id.jpg")
        await ctx.respond(file=image)

    @rr.command(description="Shows All Of The Reactions Roles In Your Guild")
    @custom_checks.has_perms("rr")
    async def list(self, ctx):
        sql = f"SELECT emoji_id, message_id, role_id, channel_id FROM reaction_roles " \
            f"WHERE guild_id=$1"
        rr_list = await self.bot.db.fetch(sql, ctx.guild.id)
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
            rr_string = f"{rr_string}» [Message](https://discordapp.com/channels/{ctx.guild.id}/{row[3]}/{row[1]}) " \
                        f"| Emoji : {emoji} | Role: {role}\n"
        embed = discord.Embed(title=f"{ctx.guild.name}'s Reaction Roles",
                              description=rr_string,
                              type="rich",)
        await ctx.respond(embed=embed)

    @discord.Cog.listener('on_raw_reaction_add')
    async def reaction_add_listener(self, payload):
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = payload.emoji
        sql = f"SELECT role_id " \
            f"FROM reaction_roles " \
            f"WHERE message_id='{payload.message_id}' and emoji_id='{emoji}'"
        role = await self.bot.db.fetch(sql)
        if role is not None:
            try:
                await payload.member.add_roles(discord.Object(int(role[0])), reason="Reaction Roles")
            except discord.Forbidden:
                try:
                    await payload.channel.respond(f"I Dont Have permission To Add Roles To {payload.member.name}")
                except discord.Forbidden:
                    pass

    @discord.Cog.listener('on_raw_reaction_remove')
    async def reaction_remove_listener(self, payload):
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = payload.emoji

        sql = f"SELECT role_id " \
            f"FROM reaction_roles " \
            f"WHERE message_id='{payload.message_id}' and emoji_id='{emoji}'"
        role = await self.bot.db.fetch(sql)
        if role is not None:
            guild = discordClient.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            try:
                await member.remove_roles(discord.Object(int(role[0])), reason="Reaction Roles")
            except discord.Forbidden:
                try:
                    await payload.respond(f"I Dont Have permission To Remove Roles From {payload.member.name}")
                except discord.Forbidden:
                    pass

    @rr.error
    @add.error
    @remove.error
    @id.error
    @list.error
    async def rr_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.respond(embed=await global_functions.create_embed(title="fail",
                                                                     description="You Do Not Have Permission To "
                                                                                 "Preform That Command"))


def setup(client):
    client.add_cog(ReactionRoles(client))

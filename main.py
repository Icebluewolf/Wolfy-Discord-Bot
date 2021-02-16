import discord
import os
from config import discordClient, cur, DB_conn
import private
import global_functions
from discord.ext import commands


def main_code():
    @discordClient.event
    async def on_ready():
        # Prints Console Message When Bot Has Finished Turning On.
        print("READY!")
        await discordClient.change_presence(status=discord.Status.online, activity=discord.Game("In The Snow"))

    @commands.is_owner()
    @commands.command(hidden=True)
    async def load(ctx, extension):
        discordClient.load_extension(f"cogs.{extension}")

    @commands.is_owner()
    @commands.command(hidden=True)
    async def unload(ctx, extension):
        discordClient.unload_extension(f"cogs.{extension}")

    @discordClient.command()
    async def ping(ctx):
        # Simple Command That Sends The Bots Ping/Latency
        """
        Pings The Bots Server
        """

        await ctx.message.delete()
        await ctx.send(embed=await global_functions.create_embed(title="",
                                                                 description=
                                                                 f"Pong :ping_pong:\nPing : `{discordClient.latency}`"),
                       delete_after=30)

    @discordClient.event
    async def on_guild_join(guild):
        # Sends a join message when the bot joins a server
        bot = guild.me
        for channel in guild.text_channels:
            bot_perms = bot.permissions_in(channel)
            if bot_perms.send_messages:
                await channel.send(f"Thanks for inviting me members of {guild}. "
                                   f"To get started an admin can run w!settings")
                break

    @discordClient.event
    async def on_member_join(member):
        # Sets Up The Users Database User Info When A User Join A Server
        cur.execute("SELECT * FROM user_data WHERE discord_user_id=%s AND guild_id=%s",
                    (str(member.id), str(member.guild.id)))
        row = cur.fetchall()
        print(row)
        if row:
            return
        else:
            await global_functions.add_user_db_row(member)

    # Simple Call And Response
    msgList = [
      ["werf", "werf"],
      ["warf", "warf"],
      ["O.o", "<:SusOwl:715254309079613543>"],
      ["o.O", "WRONG WAY!"],
    ]

    async def on_message(message):
        # Don't check your own hehe
        if message.author == discordClient.user:
            return

        # Do simple throw back messages
        for msgInfo in msgList:
            if msgInfo[0] == message:
                await message.channel.send(msgInfo[1])
                return

    # Run The Bot And Load Cogs
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            discordClient.load_extension(f"cogs.{filename[:-3]}")

    discordClient.load_extension('jishaku')
    discordClient.run(private.clientSecret)


if __name__ == "__main__":
    main_code()

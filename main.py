import discord
from config import discordClient, cur, DB_conn
import private
import whitelist_command, poll_function, per_guild_config, lottery


@discordClient.event
async def on_ready():
  # Prints Console Message When Bot Has Finished Turning On.
  print("READY!")


@discordClient.command()
async def ping(ctx):
  """
  Pings The Bots Server
  """

  await ctx.send("Pong :ping_pong:\n`Ping : " + str(discordClient.latency) + "`")


@discordClient.event
async def on_guild_join(guild):
    """Sets up the guilds Database Entry When The Bot Joins A Guild"""
    guild = str(guild.id)
    cur.execute(
        'INSERT INTO guild_settings (bypass_roles_id, lottery, poll, whitelist, lottery_access_roles_id, '
        'poll_access_roles_id, whitelist_access_roles_id, "MC_hosting_link", "MC_API_key", "MC_server_id", '
        'autorespond, guild_id) '
        'VALUES (NULL, True, True, False, NULL, NULL, NULL, NULL, NULL, NULL, True, %s);', (guild,))
    DB_conn.commit()


@discordClient.event
async def on_member_join(member):
    """
    Sets Up The Users Database User Info
    """
    cursor = cur.execute("SELECT * FROM user_data WHERE discord_user_id=%s AND guild_id=%s",
                         (str(member.id), str(member.guild.id)))
    row = cur.fetchall()
    print(row)
    if row:
        return
    else:
        cur.execute(
            "INSERT INTO user_data (discord_user, discord_user_id, whitelist, guild_id) "
            "VALUES ('{}', {}, True, {});".format(member.name + "#" + member.discriminator,
                                                  member.id,
                                                  member.guild.id))
        DB_conn.commit()


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

discordClient.run(private.clientSecret)

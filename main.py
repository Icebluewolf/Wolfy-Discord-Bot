import discord
import poll_function
import ClientSecret
import psycopg2
from discord.ext import commands
from pydactyl import PterodactylClient


discordClient = commands.Bot(command_prefix="w")
MCClient = PterodactylClient("https://panel.primedhosting.com/", ClientSecret.PH_API_KEY)
DB_conn = psycopg2.connect("dbname=Wolfy-Bot user=" + ClientSecret.DBuser + " password=" + ClientSecret.DBpassword)

cur = DB_conn.cursor()
srv_id = "bf9213e8"


@discordClient.event
async def on_ready():
    print("READY!")


@discordClient.command()
async def ping(ctx):
    """
    Pings The Bots Server
    """

    await ctx.send("Pong :ping_pong:\n`Ping : " + str(discordClient.latency) + "`")


@discordClient.command()
async def poll(ctx, *, content):
    await poll_function.poll(ctx, content)


@discordClient.command()
async def whitelist(ctx, *, content):
    """Allows A User To Whitelist Themselves On The Connected MC Server"""
    if content.strip == "":
        print("cancelled")
        return
    cur.execute("select count(*) from used_command where user_id = %s", (str(ctx.author.id),))
    is_present = cur.fetchone()[0]
    print(is_present)
    print(ctx.author.id)
    if is_present > 0 and ctx.author.id != 451848182327148554:
        await ctx.send("You Have Already Whitelisted An Account.\n"
                       "If You Changed Your Account Name Or Got A New Account Please Contact A Staff Member.")
        return
    else:
        cur.execute(
            "INSERT INTO used_command (discord_user, user_id, whitelist) "
            "VALUES ('{}', {}, True);".format(ctx.author.name + "#" + ctx.author.discriminator, ctx.author.id))
        DB_conn.commit()
        # MCClient.client.send_console_command(srv_id, "whitelist add " + content)
        await ctx.send("The User {} Has Been Added To The Whitelist".format(content))


@whitelist.error
async def whitelist_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Put Your MC Username After The Command To Whitelist Yourself On The MC Server")

msgList = [
    ["werf","werf"],
    ["warf","warf"],
    ["O.o","<:SusOwl:715254309079613543>"],
    ["o.O","WRONG WAY!"],
]
        
async def on_message(message):
    #Don't check your own hehe
    if message.author == discordClient.user:
        return
    
    #Do the poll
    if message.content.startswith("wpoll"):
        await poll.poll(message, message.author)
        
    #Do simple throw back messsages
    for msgInfo in msgList:
        if msgInfo[0] == message:
            await message.channel.send(msgInfo[1])
            return
#     if message.author == discordClient.user:
#         return
#     if message.content.startswith("wpoll"):
#         await poll.poll(message, message.author)
#     if message.content.startswith("O.o"):
#         if str(message.author.id) == 521367820957777923 or 451848182327148554:
#             await message.channel.send("Hehe " + str(message.author)[:-5] + " STINKY <:SusOwl:715254309079613543> ")
#         else:
#             await message.channel.send("hehe <:SusOwl:715254309079613543>")
#     if message.content.startswith("werf"):
#         await message.channel.send("werf")
#     if message.content.startswith("warf"):
#         await message.channel.send("warf")


discordClient.run(ClientSecret.clientSecret)

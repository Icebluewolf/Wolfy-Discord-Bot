import discord
from config import discordClient
import private


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

discordClient.run(ClientSecret.clientSecret)

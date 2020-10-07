import discord
from config import discordClient
import ClientSecret


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


    
    
#############################
#SIMPLE MESSAGE AND CALLBACK#
#############################

def parse(inpStr: str):
    strList = [""]
    strListIndex = 0
    lastOneAlpha = False
    for char in inpStr:
        isAlpha = False
        for alpha in alphabet:
            if char == alpha:
            isAlpha = True
            break
        if (not isAlpha) and lastOneAlpha:
            strListIndex += 1
            strList.append("")
            lastOneAlpha = False
        elif isAlpha:
            lastOneAlpha = True
            strList[strListIndex] += char
    if not lastOneAlpha:
        strList.pop()
    return(strList)

callCommands = [
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
    parsedMessage = parse(message)
    for phrase in parsedMessage:
        for command in callCommands:
        if command[0] == phrase.lower():
            await message.channel.send(command[1])
            return

discordClient.run(ClientSecret.clientSecret)

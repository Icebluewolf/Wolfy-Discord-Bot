import discord
import datetime
import asyncio
import re
from discord.ext import commands
from config import discordClient

client = discord.Client()


emojis = "🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹".split()
for i in emojis:
    i.replace(' ', '')

days = 0
hours = 0
minutes = 0
timeSeconds = 0


@discordClient.command()
async def poll(ctx, *, content):
    """
    Makes A Poll That Users Can Vote On.
    """
    ctx.message.delete
    global seconds
    msg = content.split(",")
    for field in msg:
        field.strip()

    try:
        timeLimitInput = msg[1]
        prevTimeLimitInputPos = 0
        for i in ["d", "h", "m", "s"]:
            timeInputPos = re.search(i, timeLimitInput)
            if timeInputPos != None:
                if int(timeLimitInput[prevTimeLimitInputPos:timeInputPos.span()[0]].strip()):
                    if i == "d":
                        days = timeLimitInput[prevTimeLimitInputPos:timeInputPos.span()[0]]
                    elif i == "h":
                        hours = timeLimitInput[prevTimeLimitInputPos:timeInputPos.span()[0]]
                    elif i == "m":
                        minutes = timeLimitInput[prevTimeLimitInputPos:timeInputPos.span()[0]]
                    elif i == "s":
                        timeSeconds = timeLimitInput[prevTimeLimitInputPos:timeInputPos.span()[0]]

                prevTimeLimitInputPos = timeInputPos.span()[0] + 1

            else:
                if i == "d":
                    days = 0
                elif i == "h":
                    hours = 0
                elif i == "m":
                    minutes = 0
                elif i == "s":
                    timeSeconds = 0

    except:
        await ctx.channel.send("Please Enter A Time In Numbers In The 3rd Position\n"
                               "Ex: 3d12h30m30s  Meaning 3 Days 12 Hours 30 Minutes And 30 Seconds")
        return

    embed = discord.Embed(title=msg[0],
                          type="rich",
                          color=0xff0000,
                          timestamp=(datetime.timedelta(days=int(days),
                                                        hours=int(hours),
                                                        minutes=int(minutes),
                                                        seconds=int(timeSeconds)) + datetime.datetime.now()))
    embed.set_footer(text="Ends")

    options = ''
    count = 0
    del msg[0]
    del msg[0]
    if len(msg) > 20 or len(msg) < 1:
        await ctx.channel.send("You Must Have 1-20 Options")
        return
    for i in msg:
        options = options + emojis[count] + "    " + i + "\n"
        count += 1
    embed.add_field(name="Options", value=options, inline=False)
    ctx = await ctx.channel.send(embed=embed)
    for i in range(len(msg)):
        await ctx.add_reaction(emojis[i])
    messageId = ctx.id

    endTime = datetime.datetime.now() + datetime.timedelta(days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(timeSeconds))
    seconds = endTime - datetime.datetime.now()
    await asyncio.sleep(seconds.total_seconds())
    ctx = await ctx.channel.fetch_message(messageId)
    winingNumber = 0
    winner = []
    for i in ctx.reactions:
        if i.count == winingNumber:
            winingNumber = i.count
            winner.append(i)
        elif i.count > winingNumber:
            winingNumber = i.count
            winner.clear()
            winner.append(i)
    if len(winner) > 1:
        resultmessage = "There was a tie between"
        for i in range(len(winner)):
            resultmessage = resultmessage + " - " + str(winner[i])
        await ctx.channel.send(resultmessage)
    else:
        await ctx.channel.send("The wining choice was " + str(winner[0]))



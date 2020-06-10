import discord
import datetime
import asyncio
import re

client = discord.Client()


emojis = "🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹".split()
for i in emojis:
    i.replace(' ', '')

days = 0
hours = 0
minutes = 0
timeSeconds = 0


async def poll(message, author):
    global seconds
    msg = message.content.split(',')
    for i in msg:
        i.strip()

    embed = discord.Embed(title=msg[1], type="rich", timestamp=datetime.datetime.utcnow(), color=0xff0000)
    try:
        timeLimitInput = msg[2]
        prevTimeLimitInputPos = 0
        for i in ["d", "h", "m", "s"]:
            timeInputPos = re.search(i, timeLimitInput)
            if timeInputPos != None:
                print(timeLimitInput[prevTimeLimitInputPos:timeInputPos.span()[0]].strip())
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
        await message.channel.send("Please Enter A Time In Numbers In The 3rd Position\nEx: 3d12h30m30s  Meaning 3 Days 12 Hours 30 Minutes And 30 Seconds")
        return

    options = ''
    count = 0
    del msg[0]
    del msg[0]
    del msg[0]
    for i in msg:
        options = options + emojis[count] + "    " + i + "\n"
        count += 1
    embed.add_field(name="Options", value=options, inline=False)
    message = await message.channel.send(embed=embed)
    for i in range(len(msg)):
        await message.add_reaction(emojis[i])
    messageId = message.id

    endTime = datetime.datetime.now() + datetime.timedelta(days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(timeSeconds))
    seconds = endTime - datetime.datetime.now()
    await asyncio.sleep(seconds.total_seconds())
    message = await message.channel.fetch_message(messageId)
    winingNumber = 0
    for i in message.reactions:
        if i.count > winingNumber:
            winingNumber = i.count
            winner = i
    await message.channel.send("The Wining Choice Was " + str(winner))



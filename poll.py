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
    #try:
    timeLimitimput = msg[2]
    timeLimit = re.search("[dhms]", timeLimitimput)
    print(timeLimit)

    count = 0
    for i in [days, hours, minutes, timeSeconds]:
        try:
            if timeLimit[count].isnumeric():
                i = timeLimit[count]
        except IndexError:
            i = 0


    #except:
        #await message.channel.send("Please Enter A Number In The 3rd Position")
        #return

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

    endTime = datetime.datetime.now() + datetime.timedelta(days=float(days), hours=float(hours), minutes=float(minutes), seconds=float(timeSeconds))
    seconds = endTime - datetime.datetime.now()
    await asyncio.sleep(seconds.total_seconds())
    message = await message.channel.fetch_message(messageId)
    winingNumber = 0
    for i in message.reactions:
        if i.count > winingNumber:
            winingNumber = i.count
            winner = i
    await message.channel.send("The Wining Choice Was " + str(winner))



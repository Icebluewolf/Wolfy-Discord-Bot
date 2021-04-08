import discord
import datetime
import asyncio
import re
import global_functions
import custom_checks
from discord.ext import commands

client = discord.Client()


emojis = "🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹".split()
for i in emojis:
    i.replace(' ', '')

days = 0
hours = 0
minutes = 0
timeSeconds = 0


class Poll(commands.Cog):

    @commands.command()
    @custom_checks.allowed_roles("poll_role", "poll_channel")
    async def poll(self, ctx, *, content):
        """
        Makes A Poll That Users Can Vote On.
        """
        await ctx.message.delete()
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
            await ctx.channel.send(embed=await global_functions.create_embed(title="error",
                                                                             description=
                                                                             "Please Enter A Time In Numbers In The 3rd Position\n"
                                                                             "Ex: 3d12h30m30s  Meaning 3 Days 12 Hours 30 Minutes And 30 Seconds"))
            return

        embed = discord.Embed(title=msg[0],
                              type="rich",
                              color=0x08D4D0,
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
            await ctx.channel.send(embed=await global_functions.create_embed(title="error",
                                                                             description="You Must Have 1-20 Options"))
            return
        for i in msg:
            options = options + emojis[count] + "    " + i + "\n"
            count += 1
        embed.add_field(name="Options", value=options, inline=False)
        ctx = await ctx.channel.send(embed=embed)
        for i in range(len(msg)):
            await ctx.add_reaction(emojis[i])
        messageId = ctx.id

        endTime = datetime.datetime.now() + datetime.timedelta(days=int(days),
                                                               hours=int(hours),
                                                               minutes=int(minutes),
                                                               seconds=int(timeSeconds))
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
            await ctx.channel.send(embed=await global_functions.create_embed(title="",
                                                                             description=resultmessage))
        else:
            await ctx.channel.send(embed=await global_functions.create_embed(title="",
                                                                             description=
                                                                             "The wining choice was " + str(winner[0])))

    @poll.error
    async def whitelist_error(self, ctx, error):
        print(f"Poll Error: {error}")
        await ctx.message.delete()
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=await global_functions.create_embed(title="fail",
                                                                     description=
                                                                     "You Do Not Have Permission To Preform That Command"))


def setup(client):
    client.add_cog(Poll(client))

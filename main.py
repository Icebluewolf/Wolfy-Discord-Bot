import discord
import poll
import ClientSecret


client = discord.Client()


@client.event
async def on_ready():
    print("READY!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("wpoll"):
        await poll.poll(message, message.author)
    if message.content.startswith("O.o"):
        if str(message.author) == "AlphDelta#5641":
            await message.channel.send("Hehe " + str(message.author) + " STINKY <:SusOwl:715254309079613543> ")
        else:
            await message.channel.send("hehe <:SusOwl:715254309079613543>")
    if message.content.startswith("werf"):
        await message.channel.send("werf")
    if message.content.startswith("warf"):
        await message.channel.send("warf")

@client.event
async def on_reaction_add(reaction, user):
    if str(user) == "Ice Wolfy#5283":
        await reaction.message.channel.send("{} has added {} to the message: {}".format(user.name, reaction.emoji, reaction.message.content))

client.run(ClientSecret.clientSecret)

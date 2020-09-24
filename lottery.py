import random
import discord

client = discord.Client

for guild in client.guilds:
    random.choice(guild.members)

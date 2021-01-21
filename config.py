import discord
import mysql.connector as mysql
import private
from pydactyl import PterodactylClient
from discord.ext import commands

# Enable Intents
intents = discord.Intents.default()
intents.members = True
# Set Discord Client (aka "bot")
discordClient = commands.Bot(command_prefix="w!", intents=intents)
# Set MC Pterodactyl Console Client
MCClient = PterodactylClient("https://panel.primedhosting.com/", private.PH_API_KEY)
# Connect To DB
DB_conn = mysql.connect(
    host="localhost",
    user=private.DBuser,
    password=private.DBpassword,
)

# Set Up Vars
cur = DB_conn.cursor()
srv_id = "bf9213e8"

# set default DB
cur.execute("USE wolfy_bot_test;")

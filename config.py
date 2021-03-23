import discord
import aiomysql
import private
from pydactyl import PterodactylClient
from discord.ext import commands, tasks

# Enable Intents
intents = discord.Intents.default()
intents.members = True
# Set Discord Client (aka "bot")
discordClient = commands.Bot(command_prefix="w!", intents=intents)
# Set MC Pterodactyl Console Client
MCClient = PterodactylClient("https://panel.primedhosting.com/", private.PH_API_KEY)
# Connect To DB
DB_conn = await aiomysql.connect(
    host=private.DB_conn,
    user=private.DBuser,
    password=private.DBpassword,
)

# Set Up Vars
cur = await DB_conn.cursor()
srv_id = "bf9213e8"


# Ping the DB every 2 hours to keep the connection open.
@tasks.loop(hours=2)
async def db_ping():
    # set default DB
    await cur.execute(f"USE {private.DB_name};")


db_ping.start()

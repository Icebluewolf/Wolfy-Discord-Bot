import psycopg2
import private
from pydactyl import PterodactylClient
from discord.ext import commands

discordClient = commands.Bot(command_prefix="w!")
MCClient = PterodactylClient("https://panel.primedhosting.com/", private.PH_API_KEY)
DB_conn = psycopg2.connect("dbname=Wolfy-Bot user=" + private.DBuser + " password=" + private.DBpassword)

cur = DB_conn.cursor()
srv_id = "bf9213e8"

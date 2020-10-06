import psycopg2
import ClientSecret
from pydactyl import PterodactylClient
from discord.ext import commands

discordClient = commands.Bot(command_prefix="w!")
MCClient = PterodactylClient("https://panel.primedhosting.com/", ClientSecret.PH_API_KEY)
DB_conn = psycopg2.connect("dbname=Wolfy-Bot user=" + ClientSecret.DBuser + " password=" + ClientSecret.DBpassword)

cur = DB_conn.cursor()
srv_id = "bf9213e8"
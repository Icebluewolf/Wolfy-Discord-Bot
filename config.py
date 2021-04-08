import discord
import private
import aiomysql
import asyncio
from pydactyl import PterodactylClient
from discord.ext import commands, tasks

# Enable Intents
intents = discord.Intents.default()
intents.members = True
# Set MC Pterodactyl Console Client
MCClient = PterodactylClient("https://panel.primedhosting.com/", private.PH_API_KEY)


class WolfyBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.loop = asyncio.get_event_loop()
        self.conn, self.db = self.loop.run_until_complete(WolfyBot.get_db())

    @staticmethod
    async def get_db():
        conn = await aiomysql.connect(host=private.DB_conn,
                         user=private.DBuser,
                         password=private.DBpassword,
                         db=private.DB_name, )
        db = await conn.cursor()
        return conn, db


# Set Discord Client (aka "bot")
discordClient = WolfyBot(command_prefix="w!", intents=intents)


class DBKeepAlive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # start keep alive
        DBKeepAlive.db_ping.start(self)

    # Ping the DB every 2 hours to keep the connection open.
    @tasks.loop(hours=2)
    async def db_ping(self):
        # set default DB
        await self.bot.db.execute(f"USE {private.DB_name};")


# Set Up Vars
srv_id = "bf9213e8"

import discord
import private
import asyncpg
import asyncio
from discord.ext import commands, tasks

# Enable Intents
intents = discord.Intents.default()
intents.members = True


class Database:

    pool = asyncio.get_event_loop().run_until_complete(asyncpg.create_pool(min_size=3, max_size=15,
                                                                           host=private.DB_conn,
                                                       user=private.DBuser,
                                                       password=private.DBpassword,
                                                       database=private.DB_name,
                                                                           timeout=60)
                                                       )

    def recycle_conn(self):
        pass
        # Database.pool.release(self.conn)

    def __init__(self) -> None:
        self.conn = asyncio.get_event_loop().run_until_complete(self._acquire())
        self.cur = None

    @staticmethod
    async def _acquire():
        conn = await Database.pool.acquire()
        return conn

    async def execute(self, sql: str, *args) -> None:
        await self.conn.execute(sql, *args)
        self.recycle_conn()

    async def fetchval(self, sql: str, *args, column=0, timeout=None):
        val = await self.conn.fetchval(sql, *args, column=column, timeout=timeout)
        self.recycle_conn()
        return val

    async def fetch(self, sql: str, *args) -> list:
        rows = await self.conn.fetch(sql, *args)
        self.recycle_conn()
        if rows:
            return rows
        else:
            return []

    # async def fetchall(self) -> list:
    #     rows = await self.cur.fetchall()
    #     self.recycle_conn()
    #     if rows:
    #         return rows
    #     else:
    #         return []


class WolfyBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = Database()


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
        # set default DB.
        await self.bot.db.execute(f"USE {private.DB_name};")

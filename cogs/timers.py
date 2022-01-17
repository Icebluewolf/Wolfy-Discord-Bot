from datetime import datetime, timedelta
import discord
import asyncio
from discord.ext import tasks, commands


CLOSE_TIMERS_IN_MINUTES = 30


class Timers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.look_for_close_times.start()

    @staticmethod
    async def format_time(time):
        if time == "forever":
            return False
        amount = ""
        future_time = datetime.now().replace(microsecond=0)
        for char in list(time):
            if char.isdigit():
                amount += char
            else:
                if char == "m":
                    future_time += timedelta(minutes=int(amount))
                elif char == "h":
                    future_time += timedelta(hours=int(amount))
                elif char == "d":
                    future_time += timedelta(days=int(amount))
                elif char == "w":
                    future_time += timedelta(weeks=int(amount))
                else:
                    return None
                amount = ""
        print(future_time)
        return future_time

    def cog_unload(self):
        self.look_for_close_times.cancel()

    @tasks.loop(minutes=CLOSE_TIMERS_IN_MINUTES)
    async def look_for_close_times(self):
        print("Started: Look for close timers")
        sql = "SELECT endtime, action, action_id, timer_id, guild_id " \
              "FROM timers " \
              "WHERE endtime <= (localtimestamp + INTERVAL '30 MINUTES');"
        for row in await self.bot.db.fetch(sql):
            print(row)
            await self.dispatch_timers(row)

    @look_for_close_times.before_loop
    async def wait_for_ready(self):
        await self.bot.wait_until_ready()
        # for i in range(1, 4):
        #     sql = f"INSERT INTO timers (action, action_id, endtime, guild_id) " \
        #           f"VALUES ('1', '000000000000000000', NOW() + INTERVAL {i * 10} SECOND, 678359965081141286)"
        #     await self.bot.db.execute(sql)
        # print("Commiting...")
        # print("added all rows")

    async def end_timer(self, timer):
        print("Timer Complete")
        sql = "DELETE FROM timers WHERE timer_id = $1;"
        await self.bot.db.execute(sql, timer[3])
        action_ids = {
            1: "tempmute",
            2: "tempban",
        }
        event_name = f"{action_ids[int(timer[1])]}_timer_complete"
        self.bot.dispatch(event_name, timer)

    async def dispatch_timers(self, timer):
        now = datetime.now()

        if timer[0] > now:
            sleep_time = (timer[0] - now).total_seconds()
            print("sleeping")
            await asyncio.sleep(sleep_time)

        await self.end_timer(timer)
        # for row in self.close_times:
        #     if row[0] < datetime.now():
        #         sql = f"DELETE FROM timers WHERE timer_id = {row[3]};"
        #         await self.bot.db.execute(sql)
        #         self.close_times.remove(row)
        #         print(f"Expired: {row[0]}")

    async def create_timer(self, endtime, action, action_id, guild_id):
        sql = f"""INSERT INTO timers (action, endtime, action_id, guild_id)
        VALUES ($1, $2, $3, $4) RETURNING timer_id;
"""
        timer_id = await self.bot.db.fetchval(sql, action, endtime, action_id, guild_id)

        if endtime - timedelta(minutes=CLOSE_TIMERS_IN_MINUTES) <= datetime.now():
            await self.dispatch_timers([endtime, action, action_id, timer_id, guild_id])

    # async def timer_ender(self, row):
    #     if row[1] == 1:
    #         self.bot.dispatch("on_tempmute_timer_complete", row[2], row[4])
    #     elif row[1] == 2:
    #         self.bot.dispatch("on_tempban_timer_complete", row[2], row[4])

    async def end_ban(self, member, guild):
        guild = self.bot.get_guild(guild)
        if guild is not None:
            member = guild.get_member(member)
            if member is not None:
                try:
                    await member.unban(reason="Temp-Ban Ended")
                except discord.Forbidden:
                    pass


def setup(client):
    client.add_cog(Timers(client))

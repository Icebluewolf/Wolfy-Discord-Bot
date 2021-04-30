import custom_checks
import discord
from datetime import datetime
from discord.ext import commands
from config import discordClient


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_action(self, title, reason, infraction_id):
        if infraction_id:
            description = f"Reason: {reason or f'No Reason Provided. Use `w!reason {infraction_id}` To Add One'}\n"
            f"Log ID: {infraction_id}"
        else:
            description = reason
        embed = discord.Embed(title=title,
                              description=description,
                              timestamp=datetime.utcnow())
        channel = self.bot.get_channel(821404230601408522)
        await channel.send(embed=embed)

    async def db_infraction(self, user_id, prosecutor_id, guild_id, infraction_type, reason=None):
        sql = f"INSERT INTO infractions (userID, prosecutorID, guildID, type, reason, datetime) " \
              f"VALUES ('{user_id}', '{prosecutor_id}', '{guild_id}', '{infraction_type}', '{reason}', NOW());" \
              f"SELECT LAST_INSERT_ID() FROM infractions;"
        await self.bot.db.execute(sql)
        if self.bot.db.lastrowid is not None:
            infraction_id = self.bot.db.lastrowid
        else:
            infraction_id = "Error"

        return infraction_id

    @commands.command()
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await ctx.guild.ban(member, reason=reason, delete_message_days=0)
        infraction_id = await self.db_infraction(member.id, ctx.author.id, ctx.guild.id, "ban", reason)
        await self.log_action(title=f"{ctx.author.name}({ctx.author.id}) Banned {member.name}({member.id})",
                                    reason=reason, infraction_id=infraction_id)

    @commands.command()
    @commands.guild_only()
    async def mute(self, ctx, member: discord.Member, time=None, *, reason=None):
        sql = "SELECT mute_role_id FROM guild_settings WHERE guild_id = %s"
        await self.bot.db.execute(sql, (ctx.guild.id,))
        role = ctx.guild.get_role(int((await self.bot.db.fetchall())[0][0]))
        if role is None:
            return await ctx.send("There Is No Mute Role. Run `w!mod mutesetup` To Create One.")
        await member.add_roles(role, reason="Staff Request Via Mute Command")
        infraction_id = await self.db_infraction(member.id, ctx.author.id, ctx.guild.id, "mute", reason)
        await self.log_action(title=f"{ctx.author.name}({ctx.author.id}) Muted {member.name}({member.id})",
                                    reason=reason, infraction_id=infraction_id)
        if time:
            timers = self.bot.get_cog("Timers")
            time = await timers.format_time(time)
            if time:
                await timers.create_timer(time, 1, member.id, ctx.guild.id)

    @commands.guild_only()
    @commands.command()
    async def unmute(self, ctx, member: discord.Member, *, reason=None):
        if member:
            sql = "SELECT mute_role_id FROM guild_settings WHERE guild_id = %s"
            await self.bot.db.execute(sql, (ctx.guild.id,))
            role = ctx.guild.get_role(int((await self.bot.db.fetchall())[0][0]))
            try:
                await member.remove_roles(role, reason=f"Unmuted By {ctx.author.name}")
                await self.log_action(title=f"{member.name}({member.id}) Was Unmuted",
                                      reason=reason or f"Manually Unmuted By {ctx.author.name}",
                                      infraction_id=None)
            except discord.Forbidden:
                print("Forbidden")

    @commands.Cog.listener()
    async def on_tempmute_timer_complete(self, timer):
        guild = self.bot.get_guild(int(timer[4]))
        if guild is not None:
            member = guild.get_member(int(timer[2]))
            if member is not None:
                sql = "SELECT mute_role_id FROM guild_settings WHERE guild_id = %s"
                await self.bot.db.execute(sql, (guild.id,))
                role = guild.get_role(int((await self.bot.db.fetchall())[0][0]))
                try:
                    await member.remove_roles(role, reason="Temp-Mute Ended")
                    await self.log_action(title=f"{member.name}({member.id}) Was Unmuted",
                                          reason="Automatically Unmuted After Tempmute Completed",
                                          infraction_id=None)
                except discord.Forbidden:
                    print("Forbidden")

    @commands.command()
    @commands.guild_only()
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        await ctx.guild.kick(user, reason=reason)
        infraction_id = await self.db_infraction(user.id, ctx.author.id, ctx.guild.id, "kick", reason)
        await self.log_action(title=f"{ctx.author.name}({ctx.author.id}) Kicked {user.name}({user.id})",
                                    reason=reason, infraction_id=infraction_id)

    @commands.command()
    @commands.guild_only()
    async def warn(self, ctx, user: discord.Member, *, reason):
        infraction_id = await self.db_infraction(user.id, ctx.author.id, ctx.guild.id, "warn", reason)
        sql = f"SELECT count(infraction_id) " \
              f"FROM infractions " \
              f"WHERE userID='{user.id}' AND guildID='{ctx.guild.id}' AND type='warn';"

        await self.bot.db.execute(sql)
        warning_count = (await self.bot.db.fetchall())[0][0]

        await self.log_action(title=f"{ctx.author.name}({ctx.author.id}) Warned {user.name}({user.id})",
                              reason=f"{reason}\nThis user now has **{warning_count}** Warns", infraction_id=infraction_id)

    @commands.command()
    @commands.guild_only()
    async def purge(self, ctx, amount, *, reason=None):
        await ctx.channel.purge(limit=int(amount) + 1)
        await self.log_action(title=f"{ctx.author.name}({ctx.author.id}) Purged {amount} Messages From {ctx.channel}",
                              reason=reason, infraction_id="N/A")

    @commands.command()
    @commands.guild_only()
    async def userpurge(self, ctx, amount, user: discord.Member, *, reason=None):
        def from_user(message):
            return message.author == user

        await ctx.channel.purge(limit=int(amount) + 1, check=from_user)
        await self.log_action(title=f"{ctx.author.name}({ctx.author.id}) Purged {amount} Of {user.name}({user.id})'s Messages In {ctx.channel}",
                              reason=reason, infraction_id="N/A")

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def mod(self, ):
        pass

    @mod.command()
    @commands.guild_only()
    async def history(self, ctx, user: discord.Member):
        sql = f"SELECT type, reason, infraction_id, datetime, prosecutorID " \
              f"FROM infractions " \
              f"WHERE userID='{user.id}' AND guildID='{ctx.guild.id}'"

        await self.bot.db.execute(sql)
        rows = (await self.bot.db.fetchall())

        embed = discord.Embed(title=f"{user.name}'s Infraction History",
                              description=f"{user.name} has had {len(rows)} infractions on this server")
        for row in rows:
            embed.add_field(name=f"{row[0].capitalize()} From {discordClient.get_user(int(row[4]))}({row[4]})",
                            value=f"```Reason: {row[1]}\nDate: {row[3]}\nInfraction ID: {row[2]}```", inline=False)

        await ctx.send(embed=embed)

    @mod.command()
    @commands.guild_only()
    async def reason(self, ctx, infraction_id, *, reason):
        sql = f"UPDATE infractions " \
              f"SET reason = '{reason}' " \
              f"WHERE infraction_id = {infraction_id} AND guildID = {ctx.guild.id}"
        await self.bot.db.execute(sql)
        await self.bot.db.execute()
        await self.log_action(f"Updated Reason For Infraction {infraction_id}", reason, infraction_id)

    @mod.command()
    @commands.guild_only()
    async def mutesetup(self, ctx, *, name=None):
        sql = "SELECT mute_role_id " \
              "FROM guild_settings " \
              "WHERE guild_id = %s"
        await self.bot.db.execute(sql, (ctx.guild.id,))
        try:
            role_id = (await self.bot.db.fetchall())[0][0]
            print(role_id)
            mutedRole = ctx.guild.get_role(int(role_id))
            muted_role_id = mutedRole.id
            print(mutedRole)
        except (IndexError, AttributeError):
            mutedRole = None

        if mutedRole is None:
            if name:
                await ctx.guild.create_role(name=name, permissions=discord.Permissions(send_messages=False,
                                                                                       add_reactions=False,
                                                                                       change_nickname=False,
                                                                                       speak=False,
                                                                                       stream=False,))
                mutedRole = discord.utils.get(ctx.guild.roles, name=name)
                muted_role_id = mutedRole.id
            else:
                await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False,
                                                                                          add_reactions=False,
                                                                                          change_nickname=False,
                                                                                          speak=False,
                                                                                          stream=False,))
                mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
                muted_role_id = mutedRole.id

            sql = "UPDATE guild_settings " \
                  "SET mute_role_id = %s " \
                  "WHERE guild_id = %s"
            await self.bot.db.execute(sql, (muted_role_id, ctx.guild.id))
            await self.bot.db.execute()

        if mutedRole > ctx.me.top_role:
            return await ctx.send("The Muted Role Is Above Mine! I Cant Edit It")

        success_list = ""
        fail_list = ""
        for channel in ctx.guild.text_channels:
            perms = channel.overwrites_for(mutedRole)
            try:
                await channel.set_permissions(mutedRole, send_messages=False)
                success_list += f"{channel.mention} "
            except discord.HTTPException:
                fail_list += f"{channel.mention} "

        embed = discord.Embed(title="Muted Role Created/Updated",
                              description="There May Have Been Some Channels That I Was Not Able To Add The Muted Role To. "
                                          "Give Me A Permission To Access All Channels To Fix This.")
        embed.add_field(name="Successful: ", value=success_list or "None")
        embed.add_field(name="Unsuccessful: ", value=fail_list or "None")
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Moderation(client))

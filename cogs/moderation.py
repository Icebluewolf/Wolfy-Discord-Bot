import custom_checks
import discord
from .utility.custom_errors import MissingSetting
from datetime import datetime
from discord.ext import commands
from config import discordClient
from discord.commands import slash_command, SlashCommandGroup, Option


class Moderation(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_action(self, guild_id, title, reason, infraction_id):

        c_id = await self.bot.db.fetchval("""
        SELECT setting_value FROM guild_settings WHERE guild_id = $1 AND setting_name = $2;
        """, guild_id, "staff.log_channel")
        if c_id:
            if infraction_id:
                description = f"Reason: {reason or f'No Reason Provided. Use `/reason {infraction_id}` To Add One'}\n"
                f"Log ID: {infraction_id}"
            else:
                description = reason
            embed = discord.Embed(title=title,
                                  description=description,
                                  timestamp=datetime.utcnow())
            channel = self.bot.get_channel(c_id)
            if channel is None:
                channel = await self.bot.fetch_channel(c_id)
            await channel.send(embed=embed)
        else:
            raise MissingSetting("staff.log_channel")

    async def db_infraction(self, user_id, prosecutor_id, guild_id, infraction_type, reason=None):
        sql = """INSERT INTO infractions ("userID", "prosecutorID", "guildID", type, reason, datetime) 
              VALUES ($1, $2, $3, $4, $5, localtimestamp) RETURNING infraction_id;"""
        infraction_id = await self.bot.db.fetchval(sql, user_id, prosecutor_id, guild_id, infraction_type, reason)
        # await self.bot.db.fetch("SELECT LAST_INSERT_ID() FROM infractions;")

        return infraction_id

    @slash_command(description="Ban A Member")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: Option(discord.Member, description="The Member To Ban"),
                  reason: Option(str, description="The Reason To Ban The Member", required=False)):
        await ctx.guild.ban(member, reason=reason, delete_message_days=0)
        infraction_id = await self.db_infraction(member.id, ctx.author.id, ctx.guild.id, "ban", reason)
        await self.log_action(ctx.guild.id, title=f"{ctx.author.name}({ctx.author.id}) Banned {member.name}"
                                                  f"({member.id})",
                              reason=reason, infraction_id=infraction_id)
        await ctx.respond(f"Successfully Banned {member.name}({member.id})")

    @slash_command(description="Prevent A Member From Speaking For A Time Or Indefinitely")
    @commands.guild_only()
    @custom_checks.has_perms("staff")
    async def mute(self, ctx, member: Option(discord.Member, description="The Member To Mute"),
                   time: Option(str, description="The Length Of Time In The Format DaysHoursMinutesSeconds ("
                                                 "3d12h30m) Default Is \"Until Unmuted\"",
                                required=False),
                   reason: Option(str, description="The Reason To Mute The Member", required=False)):
        await ctx.defer()
        sql = "SELECT setting_value FROM guild_settings WHERE guild_id = $1 AND setting_name = $2"
        rows = await self.bot.db.fetch(sql, ctx.guild.id, "staff.mute_role_id")
        if rows:
            role = ctx.guild.get_role(int(rows[0]["setting_value"]))
            # if role is None:
            #     raise commands.InvalidRoleSetting(ctx, "staff.role")
            await member.add_roles(role, reason="Staff Request Via Mute Command")
            infraction_id = await self.db_infraction(member.id, ctx.author.id, ctx.guild.id, "mute", reason)
            await self.log_action(ctx.guild.id,
                                  title=f"{ctx.author.name}({ctx.author.id}) Muted {member.name}({member.id})",
                                  reason=reason, infraction_id=infraction_id)
            if time:
                timers = self.bot.get_cog("Timers")
                time = await timers.format_time(time)
                if time:
                    await timers.create_timer(time, 1, member.id, ctx.guild.id)
            await ctx.respond(f"Successfully Muted {member.name}({member.id})")
        else:
            raise MissingSetting("staff.mute_role_id", "You Are Missing The %s Setting. Set An ID Or Run /mod "
                                                       "mutesetup")

    @commands.guild_only()
    @slash_command(description="Unmutes A User If They Are Muted For A Time Or Indefinitely")
    @custom_checks.has_perms("staff")
    async def unmute(self, ctx,
                     member: Option(discord.Member, description="The Member To Unmute"),
                     reason: Option(str, description="The Reason To Unmute The Member", required=False)):
        if member:
            sql = "SELECT setting_value FROM guild_settings WHERE guild_id = $1 AND setting_name = $2"
            role = await self.bot.db.fetch(sql, ctx.guild.id, "staff.mute_role_id")
            if role:
                role = ctx.guild.get_role(int(role[0]["setting_value"]))
                try:
                    await member.remove_roles(role, reason=f"Unmuted By {ctx.author.name}")
                    await self.log_action(ctx.guild.id, title=f"{member.name}({member.id}) Was Unmuted",
                                          reason=reason or f"Manually Unmuted By {ctx.author.name}",
                                          infraction_id=None)
                    await ctx.respond(f"Successfully Unmuted {member.name}({member.id})")
                except discord.Forbidden:
                    pass
            else:
                raise MissingSetting("staff.mute_role_id", "You Are Missing The %s Setting. Set An ID Or Run /mod "
                                                           "mutesetup")

    @discord.Cog.listener()
    async def on_tempmute_timer_complete(self, timer):
        guild = self.bot.get_guild(int(timer[4]))
        if guild is not None:
            member = guild.get_member(int(timer[2]))
            if member is not None:
                sql = "SELECT setting_value FROM guild_settings WHERE guild_id = $1 AND setting_name = $2;"
                role = await self.bot.db.fetch(sql, guild.id, "staff.mute_role_id")
                if role:
                    role = guild.get_role(int(role[0]["setting_value"]))
                    try:
                        await member.remove_roles(role, reason="Temp-Mute Ended")
                        await self.log_action(timer[5], title=f"{member.name}({member.id}) Was Unmuted",
                                              reason="Automatically Unmuted After Tempmute Completed",
                                              infraction_id=None)
                    except discord.Forbidden:
                        pass
                else:
                    await self.log_action(timer[5], title=f"{member.name}({member.id}) Was __Not__ Unmuted",
                                          reason="You Are Missing The staff.mute_role_id Setting. Set An ID Or Run /mod"
                                                 " mutesetup",
                                          infraction_id=None)

    @slash_command(description="Kick A Member From The Guild, Will Not Prevent Rejoining")
    @commands.guild_only()
    @custom_checks.has_perms("staff")
    async def kick(self, ctx,
                   member: Option(discord.Member, description="The Member To Kick"),
                   reason: Option(str, description="The Reason To Kick The Member", required=False)):
        await ctx.guild.kick(member, reason=reason)
        infraction_id = await self.db_infraction(member.id, ctx.author.id, ctx.guild.id, "kick", reason)
        await self.log_action(ctx.guild.id,
                              title=f"{ctx.author.name}({ctx.author.id}) Kicked {member.name}({member.id})",
                              reason=reason, infraction_id=infraction_id)
        await ctx.respond(f"Successfully Kicked {member.name}({member.id})")

    @slash_command(description="Warn A Member To Note Minor Bad Behavior")
    @commands.guild_only()
    @custom_checks.has_perms("staff")
    async def warn(self, ctx,
                   member: Option(discord.Member, description="The Member To Warn"),
                   reason: Option(str, description="The Reason To Warn The Member", required=False)):
        infraction_id = await self.db_infraction(member.id, ctx.author.id, ctx.guild.id, "warn", reason)
        sql = """SELECT count(infraction_id) 
              FROM infractions 
              WHERE "userID"=$1 AND "guildID"=$2 AND type='warn';"""

        warning_count = (await self.bot.db.fetch(sql, member.id, ctx.guild.id))[0]["count"]

        await self.log_action(ctx.guild.id,
                              title=f"{ctx.author.name}({ctx.author.id}) Warned {member.name}({member.id})",
                              reason=f"{reason}\nThis member now has **{warning_count}** Warns",
                              infraction_id=infraction_id)
        await ctx.respond(f"Successfully Warned {member.name}({member.id})")

    @slash_command(description="Delete Multiple Message From The Channel At Once")
    @commands.guild_only()
    @custom_checks.has_perms("staff")
    async def purge(self, ctx,
                    amount: Option(int, max_value=100, min_value=1, description="The Amount Of Message To Delete"),
                    reason: Option(str, description="The Reason To Purge The Messages", required=False)):
        await ctx.channel.purge(limit=int(amount))
        await self.log_action(ctx.guild.id, title=f"{ctx.author.name}({ctx.author.id}) Purged {amount} Messages From "
                                                  f"{ctx.channel}",
                              reason=reason, infraction_id="N/A")
        await ctx.respond(f"Successfully Purged {amount} Messages")

    @slash_command(description="Delete Multiple Messages In The Channel From A Specific Member")
    @commands.guild_only()
    @custom_checks.has_perms("staff")
    async def userpurge(self, ctx,
                        amount: Option(int, max_value=100, min_value=1, description="The Amount Of Message To Delete"),
                        member: Option(discord.Member, "The Member Whose Message To Purge"),
                        reason: Option(str, description="The Reason To Purge The Member Messages", required=False)):
        def from_user(message):
            return message.author == member

        await ctx.channel.purge(limit=int(amount), check=from_user)
        await self.log_action(ctx.guild.id,
                              title=f"""{ctx.author.name}({ctx.author.id}) Purged {amount} Of {member.name}
                                        ({member.id})'s Messages In {ctx.channel}""",
                              reason=reason, infraction_id="N/A")
        await ctx.respond(f"Successfully Purged {amount} Messages From {member.name}({member.id})")

    mod = SlashCommandGroup("mod", "Utility Functions For Mods")
    # @commands.group(invoke_without_command=True)
    # @commands.guild_only()
    # @custom_checks.has_perms("staff")
    # async def mod(self, ctx):
    #     pass

    @mod.command(description="Shows The Punishments For A Member")
    @commands.guild_only()
    @custom_checks.has_perms("staff")
    async def history(self, ctx,
                      user: Option(discord.Member, description="The Member Whose Punishments To Show")):
        sql = """SELECT type, reason, infraction_id, datetime, "prosecutorID" 
              FROM infractions 
              WHERE "userID"=$1 AND "guildID"=$2"""

        rows = (await self.bot.db.fetch(sql, user.id, ctx.guild.id))
        rows = rows[::-1]

        embed = discord.Embed(title=f"{user.name}'s Infraction History",
                              description=f"{user.name} has had {len(rows)} infractions on this server")
        for row in rows:
            embed.add_field(name=f"{row[0].capitalize()} From {discordClient.get_user(int(row[4]))}({row[4]})",
                            value=f"```Reason: {row[1]}\nDate: {row[3]}\nInfraction ID: {row[2]}```", inline=False)

        await ctx.respond(embed=embed)

    @mod.command(description="Add Or Update A Reason For An Infraction")
    @commands.guild_only()
    @custom_checks.has_perms("staff")
    async def reason(self, ctx,
                     infraction_id: Option(int, description="The ID For The Infraction To Update"),
                     reason: Option(str, description="The New Reason")):
        sql = """UPDATE infractions 
              SET reason = $1 
              WHERE infraction_id = $2 AND "guildID" = $3"""
        await self.bot.db.execute(sql, str(reason), infraction_id, ctx.guild.id)
        await self.log_action(ctx.guild.id, f"Updated Reason For Infraction {infraction_id}", reason, infraction_id)
        await ctx.respond(f"Successfully Updated The Reason For Infraction {infraction_id}")

    @mod.command(description="Set Up A Working Mute Role For The Guild")
    @commands.guild_only()
    @custom_checks.has_perms("staff")
    async def mutesetup(self, ctx,
                        name: Option(str, description="The Name Of The Muted Role Defaults To \"Muted\"",
                                     required=False, default="Muted")):
        sql = """SELECT setting_value 
              FROM guild_settings 
              WHERE guild_id = $1 AND setting_name = $2"""
        try:
            role_id = (await self.bot.db.fetch(sql, ctx.guild.id, "staff.mute_role_id"))[0][0]
            muted_role = ctx.guild.get_role(int(role_id))
        except (IndexError, AttributeError):
            muted_role = None

        if muted_role is None:
            await ctx.guild.create_role(name=name, permissions=discord.Permissions(send_messages=False,
                                                                                   add_reactions=False,
                                                                                   change_nickname=False,
                                                                                   speak=False,
                                                                                   stream=False,))
            muted_role = discord.utils.get(ctx.guild.roles, name=name)
            muted_role_id = muted_role.id

            sql = """INSERT INTO guild_settings(guild_id, setting_name, setting_value) 
                  VALUES ($1, $2, $3) 
                  ON CONFLICT (guild_id, setting_name) DO UPDATE SET   
                  setting_value = $4;"""
            await self.bot.db.execute(sql, ctx.guild.id, "staff.mute_role_id", str(muted_role_id),
                                      str(muted_role_id))

        if muted_role > ctx.me.top_role:
            return await ctx.respond("The Muted Role Is Above Mine! I Cant Edit It")

        success_list = ""
        fail_list = ""
        for channel in ctx.guild.text_channels:
            try:
                await channel.set_permissions(muted_role, send_messages=False)
                success_list += f"{channel.mention} "
            except discord.HTTPException:
                fail_list += f"{channel.mention} "

        embed = discord.Embed(title="Muted Role Created/Updated",
                              description="There May Have Been Some Channels That I Was Not Able To Add The "
                                          "Muted Role To. Give Me A Permission To Access All Channels To Fix This.")
        embed.add_field(name="Successful: ", value=success_list or "None")
        embed.add_field(name="Unsuccessful: ", value=fail_list or "None")
        await ctx.respond(embed=embed)


def setup(client):
    client.add_cog(Moderation(client))

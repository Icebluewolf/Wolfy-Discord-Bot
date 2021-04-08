from config import discordClient
from discord.ext import commands
import asyncio
import global_functions


module_string = ""
module_list = [("lottery", "On"), ("poll", "On"), ("whitelist", "Off")]
for i in module_list:
    module_string = module_string + "\n**{}** : {}".format(i[0], i[1])


class GuildSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx, *, setting=None):
        """
        Allows Server Admins To Change How Functions Of The Bot Work
        Usage: w!settings [setting] [option]
        """

        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        async def modify_database(guild: str, id_list, setting, key, identifier_column):
            for id in id_list:
                sql = f"INSERT INTO {setting} ({key}, guild_id, {identifier_column}) " \
                    f"VALUES (true, {guild}, {id}) " \
                    f"ON DUPLICATE KEY UPDATE " \
                    f"{key}=true;"
                # sql = f"UPDATE {setting} SET {key}={value} WHERE guild_id =%s"
                self.bot.db.execute(sql, ())
            self.bot.db.commit()

        async def get_role_name(column):
            if column == []:
                return "Admins Only"
            output = ""
            for role_id in column:
                output = output + ctx.guild.get_role(int(role_id)).name + ", "
            return output

        async def get_channel_name(column):
            if column == []:
                return "No Channels"
            output = ""
            for channel_id in column:
                print(channel_id)
                output = output + ctx.guild.get_channel(int(channel_id)).mention + ", "
            return output

        async def get_setting(ctx, module=None, var=None):
            if not module:
                if var == "channel":
                    message = f"Type The Channel Names(#channel) You Want To Let Use The **{module}** Module. " \
                              f"(Separate with `,`) Type \"all\" For All Channels."
                elif var == "role":
                    message = f"Type The Role Names(Not Ping) You Want To Let Use The **{module}** Module. " \
                          f"(Separate with `,`) Type \"everyone\" For Everyone."
            else:
                print(var)
                message = f"**{module.capitalize()}**\n" \
                    f"Roles :\t {await get_role_name(var[0])}\n" \
                    f"Channels :\t {await get_channel_name(var[1])}\n" \
                    f"*Type The Setting You Want To Change*"

            await ctx.send(embed=await global_functions.create_embed(title="",
                                                                     description=message,),
                           delete_after=30)

            answer = await discordClient.wait_for("message", timeout=30, check=check)
            await answer.delete()
            return answer.content.lower()

        async def get_roles(ctx, setting, module):
            denied_roles = ""
            verified_roles = []
            setting = setting.split(",")
            for response in setting:
                response = response.strip()
                for role in ctx.guild.roles:
                    if response == "everyone":
                        verified_roles.append(ctx.guild.roles[0].id)
                        break
                    elif response == role.name.lower():
                        verified_roles.append(role.id)
                        break
                else:
                    denied_roles = f"{denied_roles} {response}"

            if verified_roles:
                await modify_database(ctx.guild.id, verified_roles, "roles", module, "role_id",)
            if denied_roles != "":
                await ctx.send(embed=await global_functions.create_embed(title="invalid",
                                                                         description=
                                                                         f"There Were A Few Roles That I Couldn't Find.\n"
                                                                         f"They Were : {denied_roles}\nCheck There Spelling And Try Again.\n"
                                                                         f"Note That This Overwrites The Old List So You Will Need To Write "
                                                                         f"The Entire List When Modifying",),
                               delete_after=30)
            else:
                await ctx.send(embed=await global_functions.create_embed(title="success",
                                                                         description="The Roles Were Added",),
                               delete_after=30)

        async def get_channels(ctx, setting, module):
            denied_channels = ""
            verified_channels = []
            setting = setting.split(",")
            print(ctx.guild.channels)
            for response in setting:
                response = response.strip()[2:-1]
                print(response)
                for channel in ctx.guild.channels:
                    if response == "all":
                        verified_channels = [None]
                        break
                    elif int(response) == channel.id:
                        verified_channels.append(channel.id)
                        break
                else:
                    denied_channels = f"{denied_channels} <#{response}>"

            if verified_channels:
                await modify_database(ctx.guild.id, verified_channels, "text_channels", module, "channel_id",)
            if denied_channels != "":
                await ctx.send(embed=await global_functions.create_embed(title="invalid",
                                                                         description=
                                                                         f"There Were A Few Channels That I Couldn't Find.\n"
                                                                         f"They Were : {denied_channels}\nCheck There Spelling And Try Again.\n"
                                                                         f"Note That This Overwrites The Old List So You Will Need To Write "
                                                                         f"The Entire List When Modifying",),
                               delete_after=30)
            else:
                await ctx.send(embed=await global_functions.create_embed(title="success",
                                                                         description="The Roles Were Added",),
                               delete_after=30)

        # Command Code Starts Here
        # Deletes Invocation Message
        await ctx.message.delete()

        # Gets Roles
        self.bot.db.execute("select role_id, bypass_role, lottery_role, poll_role, whitelist_role, rr_role "
                    "from roles "
                    "where guild_id = %s", (str(ctx.guild.id),))
        rows = self.bot.db.fetchall()

        bypass_roles = []
        lottery_roles = []
        poll_roles = []
        whitelist_roles = []
        rr_roles = []
        for row in rows:
            if row[1]:
                bypass_roles.append(row[0])
                continue
            if row[2]:
                lottery_roles.append(row[0])
            if row[3]:
                poll_roles.append(row[0])
            if row[4]:
                whitelist_roles.append(row[0])
            if row[5]:
                rr_roles.append(row[0])

        # Gets Channels
        self.bot.db.execute("select channel_id, lottery_channel, poll_channel, whitelist_channel, rr_channel "
                    "from text_channels "
                    "where guild_id = %s", (str(ctx.guild.id),))
        rows = self.bot.db.fetchall()

        lottery_channels = []
        poll_channels = []
        whitelist_channels = []
        rr_channels = []
        for channel in rows:
            if channel[1]:
                lottery_channels.append(channel[0])
            if channel[2]:
                poll_channels.append(channel[0])
            if channel[3]:
                whitelist_channels.append(channel[0])
            if channel[4]:
                rr_channels.append(channel[0])

        # Checks If There Was A Specified Setting To Start On
        setting_input_1 = ""
        if setting:
            setting = setting.split(" ")
            setting_input_0 = setting[0]
            if len(setting) >= 2:
                setting_input_1 = setting[1]
        # If Not Prompt The User To Define One
        else:
            await ctx.send(embed=await global_functions.create_embed(title="",
                                                                     description=
                                                                     "**Type The Name Of The Setting You "
                                                                     "Want To Change**\n"
                                                                     "Lottery\n"
                                                                     "Poll\n"
                                                                     "Whitelist\n"
                                                                     "Reaction Roles (rr)\n"
                                                                     "Bypass `NOTE: These Roles Bypass All Permissions`"),
                           delete_after=30)

            try:
                setting_input_0 = await discordClient.wait_for("message", timeout=30, check=check)
                await setting_input_0.delete()
                setting_input_0 = setting_input_0.content
            except asyncio.TimeoutError:
                await ctx.message.delete()
                return

        # Enter All Of The Command Specific Data Into The Functions
        if setting_input_0 == "lottery":
            if not setting_input_1:
                setting_input_1 = await get_setting(ctx, "lottery", [lottery_roles, lottery_channels])

            if setting_input_1 == "roles":
                setting = await get_setting(ctx=ctx, var="role")
                await get_roles(ctx, setting, "lottery_role")
            elif setting_input_1 == "channels":
                setting = await get_setting(ctx=ctx, var="channel")
                await get_roles(ctx, setting, "lottery_channel")

            else:
                await ctx.send(embed=await global_functions.create_embed(title="invalid",
                                                             description=f"That Is Not An Option"),
                               delete_after=30)

        # Split (This Is So I Can Keep My If Statements Apart)

        elif setting_input_0 == "poll":
            if not setting_input_1:
                setting_input_1 = await get_setting(ctx, "poll", [poll_roles, poll_channels])

            if setting_input_1 == "roles":
                # await get_setting(ctx, "poll", "role")
                setting = await get_setting(ctx=ctx, var="role")
                await get_roles(ctx, setting, "poll_role")
            elif setting_input_1 == "channels":
                setting = await get_setting(ctx=ctx, var="channel")
                await get_channels(ctx, setting, "poll_channel")

            else:
                await ctx.send(embed=await global_functions.create_embed(title="invalid",
                                                             description=f"That Is Not An Option"),
                               delete_after=30)

        # Split (This Is So I Can Keep My If Statements Apart)

        elif setting_input_0 == "whitelist":
            if not setting_input_1:
                setting_input_1 = await get_setting(ctx, "whitelist", [whitelist_roles, whitelist_channels])

            if setting_input_1 == "roles":
                setting = await get_setting(ctx=ctx, var="role")
                await get_roles(ctx, setting, "whitelist_role")
            elif setting_input_1 == "channels":
                setting = await get_setting(ctx=ctx, var="channel")
                await get_channels(ctx, setting, "whitelist_channel")

            else:
                await ctx.send(embed=await global_functions.create_embed(title="invalid",
                                                             description=f"That Is Not An Option"),
                               delete_after=30)

        elif setting_input_0 == "rr":
            if not setting_input_1:
                setting_input_1 = await get_setting(ctx, "rr", [rr_roles, rr_channels])

            if setting_input_1 == "roles":
                setting = await get_setting(ctx=ctx, var="role")
                await get_roles(ctx, setting, "rr_role")
            elif setting_input_1 == "channels":
                setting = await get_setting(ctx=ctx, var="channel")
                await get_channels(ctx, setting, "rr_channel")

            else:
                await ctx.send(embed=await global_functions.create_embed(title="invalid",
                                                             description=f"That Is Not An Option"),
                               delete_after=30)

        elif setting_input_0 == "bypass":
            setting = await get_setting(ctx, "bypass", bypass_roles)
            await get_roles(ctx, setting, "bypass_role")

        else:
            await ctx.send(embed=await global_functions.create_embed(title="invalid",
                                                                     description=
                                                                     "That Is Not A Setting. Run The Command "
                                                                     "`w!settings` To Get A List Of All Settings.",),
                           delete_after=30)

    @settings.error
    async def settings_error(self, ctx, error):
        print(f"Settings Error: {error}")
        if isinstance(error, commands.CommandInvokeError):
            pass
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(embed=await global_functions.create_embed(title="fail",
                                                                     description=
                                                                     "You Must Have Admin To Use This Command",),
                           delete_after=30)


def setup(client):
    client.add_cog(GuildSettings(client))

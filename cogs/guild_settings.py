from config import discordClient, DB_conn, cur
from discord.ext import commands
import asyncio
import global_functions


module_string = ""
module_list = [("lottery", "On"), ("poll", "On"), ("whitelist", "Off")]
for i in module_list:
    module_string = module_string + "\n**{}** : {}".format(i[0], i[1])


class GuildSettings(commands.Cog):

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx, *, setting=None):
        """
        Allows Server Admins To Change How Functions Of The Bot Work
        Usage: w!settings [setting] [option]
        """

        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        async def modify_database(guild, key, value):
            guild = str(guild)
            sql = f"UPDATE guild_settings SET {key}={value} WHERE guild_id =%s"
            cur.execute(sql, (guild,))
            DB_conn.commit()

        async def get_role_name(column):
            if column is None:
                return "Admins Only"
            output = ""
            for role_id in column:
                output = output + ctx.guild.get_role(int(role_id)).name + ", "
            return output

        async def get_setting(ctx, prompt):
            await ctx.send(embed=await global_functions.create_embed(title="",
                                                                     description=prompt,),
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
                await modify_database(ctx.guild.id, module, f"ARRAY{verified_roles}")
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

        # Command Code Starts Here
        # Deletes Invocation Message
        await ctx.message.delete()

        cur.execute("select bypass_roles_id, lottery_access_roles_id, poll_access_roles_id, whitelist_access_roles_id "
                    "from guild_settings where guild_id = %s", (str(ctx.guild.id),))
        row = cur.fetchall()[0]

        # Checks If There Was A Specified Setting To Start On
        setting_input_1 = ""
        if setting:
            setting = setting.split(" ")
            setting_input_0 = setting[0]
            if len(setting) >= 2:
                setting_input_1 = setting[1]
        else:
            await ctx.send(embed=await global_functions.create_embed(title="",
                                                                     description=
                                                                     "**Type The Name Of The Setting You "
                                                                     "Want To Change**\n"
                                                                     "Lottery\n"
                                                                     "Poll\n"
                                                                     "Whitelist\n"
                                                                     "Bypass NOTE: These Roles Bypass All Permissions"),
                           delete_after=30)

            try:
                setting_input_0 = await discordClient.wait_for("message", timeout=30, check=check)
                await setting_input_0.delete()
                setting_input_0 = setting_input_0.content
            except asyncio.TimeoutError:
                await ctx.message.delete()
                return

        if setting_input_0 == "lottery":
            if not setting_input_1:
                setting_input_1 = await get_setting(ctx, f"**Lottery**\n"
                                            f"Roles  : {await get_role_name(row[1])}\n"
                                            f"**Type The Setting You Want To Change**")

            if setting_input_1 == "roles":
                setting = await get_setting(ctx, "**Type The Role Names(Not Ping) You Want To Let Use The Lottery."
                                                 "(Separate with `,`) Type \"everyone\" For Everyone.**")
                await get_roles(ctx, setting, "lottery_access_roles_id")

            else:
                await ctx.send(embed=await global_functions.create_embed(title="invalid",
                                                             description=f"That Is Not An Option"),
                               delete_after=30)

        # Split (This Is So I Can Keep My If Statements Apart)

        elif setting_input_0 == "poll":
            if not setting_input_1:
                setting_input_1 = await get_setting(ctx, f"**Poll**\n"
                                            f"Roles  : {await get_role_name(row[2])}\n"
                                            f"**Type The Setting You Want To Change**")

            if setting_input_1 == "roles":
                setting = await get_setting(ctx,
                                            "**Type The Role Names You Want To Let Use The Poll.(Separate with `,`)"
                                            " Type \"everyone\" For Everyone.**")
                await get_roles(ctx, setting, "poll_access_roles_id")

            else:
                await ctx.send(embed=await global_functions.create_embed(title="invalid",
                                                             description=f"That Is Not An Option"),
                               delete_after=30)

        # Split (This Is So I Can Keep My If Statements Apart)

        elif setting_input_0 == "whitelist":
            if not setting_input_1:
                setting_input_1 = await get_setting(ctx, f"**Whitelist**\n"
                                            f"Roles  : {await get_role_name(row[3])}\n"
                                            f"**Type The Setting You Want To Change**")

            if setting_input_1 == "roles":
                setting = await get_setting(ctx,
                                            "**Type The Role Names You Want To Let Use The Whitelist."
                                            "(Separate with `,`) Type \"everyone\"k For Everyone.**")
                await get_roles(ctx, setting, "whitelist_access_roles_id")

            else:
                await ctx.send(embed=await global_functions.create_embed(title="invalid",
                                                             description=f"That Is Not An Option"),
                               delete_after=30)

        elif setting_input_0 == "bypass":
            setting = await get_setting(ctx,
                                        "**Type The Role Names You Want To Bypass ALL Permissions."
                                        "(Separate with `,`) Type \"everyone\" For Everyone.**")
            await get_roles(ctx, setting, "bypass_roles_id")

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

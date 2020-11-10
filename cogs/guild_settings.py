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
    async def settings(self, ctx, setting=None):
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
                    if response == role.name:
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
        if setting:
            setting_input = setting
        else:
            await ctx.send(embed=await global_functions.create_embed(title="",
                                                                     description=
                                                                     "**Type The Name Of The Setting You "
                                                                     "Want To Change**\n"
                                                                     "Lottery\n"
                                                                     "Poll\n"
                                                                     "Whitelist\n"),
                           delete_after=30)

            try:
                setting_input = await discordClient.wait_for("message", timeout=30, check=check)
                await setting_input.delete()
                setting_input = setting_input.content
            except asyncio.TimeoutError:
                await ctx.message.delete()
                return

        if setting_input == "lottery":
            setting = await get_setting(ctx, f"**Lottery**\n"
                                        f"Module : {module_list[0][1]}\n"
                                        f"Roles  : {await get_role_name(row[1])}\n"
                                        f"**Type The Setting You Want To Change**")
            if setting == "module":
                setting = await get_setting(ctx, "**Would You Like To Turn This Module On Or Off**")
                if setting == "off":
                    await modify_database(ctx.guild.id, "lottery", "False")
                elif setting_input == "on":
                    await modify_database(ctx.guild.id, "lottery", "True")

            elif setting == "roles":
                setting = await get_setting(ctx, "**Type The Role Names(Not Ping) You Want To Let Use The Lottery."
                                                 "(Separate with `,`) Leave Blank For Everyone.**")
                await get_roles(ctx, setting, "lottery_access_roles_id")

        elif setting_input == "poll":
            setting = await get_setting(ctx, f"**Poll**\n"
                                        f"Module : {module_list[1][1]}\n"
                                        f"Roles  : {await get_role_name(row[2])}\n"
                                        f"**Type The Setting You Want To Change**")
            if setting == "module":
                setting = await get_setting(ctx, "**Would You Like To Turn This Module On Or Off**")
                if setting == "off":
                    await modify_database(ctx.guild.id, "poll", "False")
                elif setting_input == "on":
                    await modify_database(ctx.guild.id, "poll", "True")

            elif setting == "roles":
                setting = await get_setting(ctx,
                                            "**Type The Role Names You Want To Let Use The Poll.(Separate with `,`)"
                                            " Leave Blank For Everyone.**")
                await get_roles(ctx, setting, "poll_access_roles_id")

        elif setting_input == "whitelist":
            setting = await get_setting(ctx, f"**Whitelist**\n"
                                        f"Module : {module_list[2][1]}\n"
                                        f"Roles  : {await get_role_name(row[3])}\n"
                                        f"**Type The Setting You Want To Change**")
            if setting == "module":
                setting = await get_setting(ctx, "**Would You Like To Turn This Module On Or Off**")
                if setting == "off":
                    await modify_database(ctx.guild.id, "whitelist", "False")
                elif setting_input == "on":
                    await modify_database(ctx.guild.id, "whitelist", "True")

            elif setting == "roles":
                setting = await get_setting(ctx,
                                            "**Type The Role Names You Want To Let Use The Whitelist."
                                            "(Separate with `,`) Leave Blank For Everyone.**")
                await get_roles(ctx, setting, "whitelist_access_roles_id")

        else:
            await ctx.send(embed=await global_functions.create_embed(title="invalid",
                                                                     description=
                                                                     "That Is Not A Setting. Run The Command "
                                                                     "`w!settings` To Get A List Of All Settings.",),
                           delete_after=30)

    @settings.error
    async def settings_error(self, ctx, error):
        print(error)
        if isinstance(error, commands.CommandInvokeError):
            pass
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(embed=await global_functions.create_embed(title="fail",
                                                                     description=
                                                                     "You Must Have Admin To Use This Command",),
                           delete_after=30)


def setup(client):
    client.add_cog(GuildSettings(client))

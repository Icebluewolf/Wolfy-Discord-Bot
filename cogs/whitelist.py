import custom_checks
import global_functions
from discord.ext import commands


class Whitelist(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.title = ""
        self.color = 0

    @commands.command()
    @custom_checks.allowed_roles("whitelist_role", "whitelist_channel")
    async def whitelist(self, ctx, *, content):
        """
        Allows A User To Whitelist Themselves On The Connected MC Server
        """
        await ctx.message.delete()
        # Return If There Is No Argument
        if content.strip == "":
            return
        # Get Users Database Entry
        sql = "select whitelist from user_data where discord_user_id = $1"
        is_present = await self.bot.db.fetch(sql, ctx.author.id)

        if is_present is None:
            await global_functions.add_user_db_row(ctx.author)
        # Check If They Have Already Used The Command Or The User Is Not A Bot Admin
        if is_present is False and ctx.author.id != 451848182327148554:
            await ctx.send(embed=await global_functions.create_embed(title="fail",
                                                                     description=
                                                                     "You Already Have An Account Whitelisted\n"
                                                                     "If You Changed Your Account Name Or Got A New "
                                                                     "Account Please Contact A Staff Member.",),
                           delete_after=30)
            return
        # Else Add Them To The Whitelist And Update Database
        else:
            user_id = str(ctx.author.id)
            sql = "UPDATE user_data SET whitelist=false WHERE discord_user_id=$1"
            await self.bot.db.execute(sql, (user_id,))
            # MCClient.client.send_console_command(srv_id, "whitelist add " + content)
            await ctx.send(embed=await global_functions.create_embed(title="Success",
                                                                     description=
                                                                     "Minecraft User {} Has Been Added To The"
                                                                     " Whitelist".format(content)),
                           delete_after=30)

    @whitelist.error
    async def whitelist_error(self, ctx, error):
        print(f"Whitelist Error: {error}")
        await ctx.message.delete()
        if isinstance(error, commands.MissingRequiredArgument):
            # If The User Did Not Specify An Argument
            await ctx.send(embed=await global_functions.create_embed(title="error",
                                                                     description=
                                                                     "Put Your MC Username After The Command To"
                                                                     " Whitelist Yourself On The MC Server"),
                           delete_after=15)
        elif isinstance(error, commands.CheckFailure):
            # If The User Dose Not Have The Required Roles To Use The Command
            await ctx.send(embed=await global_functions.create_embed(title="fail",
                                                                     description=
                                                                     "You Must Be Level 10 To Access"
                                                                     " This Command"),
                           delete_after=15)


def setup(client):
    client.add_cog(Whitelist(client))


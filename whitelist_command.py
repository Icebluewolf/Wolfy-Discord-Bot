from config import discordClient, MCClient, DB_conn, cur, srv_id
from discord.ext import commands


@discordClient.command()
@commands.has_role("712329562763165758")
async def whitelist(ctx, *, content):
    """
    Allows A User To Whitelist Themselves On The Connected MC Server
    """
    # Return If There Is No Argument
    if content.strip == "":
        print("cancelled")
        return
    # Get Users Database Entry
    cur.execute("select count(*) from user_data where user_id = %s", (str(ctx.author.id),))
    is_present = cur.fetchone()[0]
    # Check If They Have Already Used The Command Or The User Is Not A Bot Admin
    if is_present > 0 and ctx.author.id != 451848182327148554:
        await ctx.send("You Have Already Whitelisted An Account.\n"
                       "If You Changed Your Account Name Or Got A New Account Please Contact A Staff Member.")
        return
    # Else Add Them To THe Whitelist And Update Database
    else:
        cur.execute(
            "INSERT INTO user_data (discord_user, user_id, whitelist) "
            "VALUES ('{}', {}, True);".format(ctx.author.name + "#" + ctx.author.discriminator, ctx.author.id))
        DB_conn.commit()
        MCClient.client.send_console_command(srv_id, "whitelist add " + content)
        await ctx.send("The User {} Has Been Added To The Whitelist".format(content))


@whitelist.error
async def whitelist_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        # If The User Did Not Specify An Argument
        await ctx.send("Put Your MC Username After The Command To Whitelist Yourself On The MC Server")
    elif isinstance(error, commands.CheckFailure):
        # If The User Dose Not Have The Required Roles To Use The Command
        await ctx.send("You Must Be Level 10 To Access This Command")

from config import discordClient, MCClient, DB_conn, cur, srv_id
from discord.ext import commands


@discordClient.command()
@commands.has_role("712329562763165758")
async def whitelist(ctx, *, content):
    """
    Allows A User To Whitelist Themselves On The Connected MC Server
    """
    if content.strip == "":
        print("cancelled")
        return
    cur.execute("select count(*) from used_command where user_id = %s", (str(ctx.author.id),))
    is_present = cur.fetchone()[0]
    print(is_present)
    print(ctx.author.id)
    if is_present > 0 and ctx.author.id != 451848182327148554:
        await ctx.send("You Have Already Whitelisted An Account.\n"
                       "If You Changed Your Account Name Or Got A New Account Please Contact A Staff Member.")
        return
    else:
        cur.execute(
            "INSERT INTO used_command (discord_user, user_id, whitelist) "
            "VALUES ('{}', {}, True);".format(ctx.author.name + "#" + ctx.author.discriminator, ctx.author.id))
        DB_conn.commit()
        MCClient.client.send_console_command(srv_id, "whitelist add " + content)
        await ctx.send("The User {} Has Been Added To The Whitelist".format(content))


@whitelist.error
async def whitelist_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Put Your MC Username After The Command To Whitelist Yourself On The MC Server")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You Must Be Level 10 To Access This Command")

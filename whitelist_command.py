import discord
from config import discordClient, MCClient, DB_conn, cur, srv_id
from discord.ext import commands


def create_embed(title, description, color=0):
    if title == "error":
        title = "There Was An Error :/"
        color = 0xE90000
    elif title == "fail":
        title = "You Cant Do That :("
        color = 0xF0FF00
    embed = discord.Embed(title=title,
                          description=description,
                          type="rich",
                          color=color,)
    return embed


@discordClient.command()
@commands.has_role("712329562763165758")
async def whitelist(ctx, *, content):
    """
    Allows A User To Whitelist Themselves On The Connected MC Server
    """
    await ctx.message.delete()
    # Return If There Is No Argument
    if content.strip == "":
        return
    # Get Users Database Entry
    cur.execute("select count(*) from user_data where user_id = %s", (str(ctx.author.id),))
    is_present = cur.fetchone()[0]
    # Check If They Have Already Used The Command Or The User Is Not A Bot Admin
    if is_present > 0 and ctx.author.id != 451848182327148554:
        await ctx.send(embed=create_embed(title="fail",
                                          description="You Already Have An Account Whitelisted\n"
                                                "If You Changed Your Account Name Or Got A New "
                                                "Account Please Contact A Staff Member.",),
                       delete_after=30)
        return
    # Else Add Them To THe Whitelist And Update Database
    else:
        cur.execute(
            "INSERT INTO user_data (discord_user, user_id, whitelist) "
            "VALUES ('{}', {}, True);".format(ctx.author.name + "#" + ctx.author.discriminator, ctx.author.id))
        DB_conn.commit()
        MCClient.client.send_console_command(srv_id, "whitelist add " + content)
        await ctx.send(embed=create_embed(title="Success",
                                          description="Minecraft User {} Has Been Added To The"
                                                      " Whitelist".format(content)),
                       delete_after=30)


@whitelist.error
async def whitelist_error(ctx, error):
    print(f"Whitelist Error: {error}")
    await ctx.message.delete()
    if isinstance(error, commands.MissingRequiredArgument):
        # If The User Did Not Specify An Argument
        await ctx.send(embed=create_embed(title="error",
                                          description="Put Your MC Username After The Command To Whitelist Yourself On"
                                                      " The MC Server"),
                       delete_after=15)
    elif isinstance(error, commands.CheckFailure):
        # If The User Dose Not Have The Required Roles To Use The Command
        await ctx.send(embed=create_embed(title="fail", description="You Must Be Level 10 To Access This Command"),
                       delete_after=15)

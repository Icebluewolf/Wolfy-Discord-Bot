from discord.ext import commands


async def has_role(setting: str, ctx: commands.Context):
    setting = setting + "_role"
    await commands.bot.db.exacute("""SELECT setting_value FROM guild_settings
            WHERE guild_id=%s AND setting_name='bypass'""", (ctx.guild.id,))
    row = await commands.bot.db.fetchone()

    if row:
        return commands.has_any_role(row.split(","))
    else:
        await commands.bot.db.exacute("""SELECT setting_value FROM guild_settings
                WHERE guild_id=%s AND setting_name=%s;""", (ctx.guild.id, setting))
        row = await commands.bot.db.fetchone()

        if row:
            return commands.has_any_role(row.split(","))
        else:
            return False


async def in_channel(setting: str, ctx: commands.Context):
    setting = setting + "_channel"
    await commands.bot.db.exacute("""SELECT setting_value FROM guild_settings
            WHERE guild_id=%s AND setting_name=%s""", (ctx.guild.id, setting))
    row = await commands.bot.db.fetchone()

    if row:
        return str(ctx.channel.id) in row.split(",")
    else:
        return False


# Checks If The User Has Permission To Use The Command And If It Is In An Approved Channel
# Any Roles In "bypass_roles_id"(Defaulted to Admins) Bypass *ALL* Restrictions
def has_perms(setting: str):
    def predicate(ctx: commands.Context):
        if commands.has_permissions(administrator=True):
            return True
        elif await has_role(setting, ctx):
            if await in_channel(setting, ctx):
                return True
            else:
                return False
        else:
            return False

    return commands.check(predicate)

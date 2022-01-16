from config import discordClient
from discord.ext import commands


# Checks If The User Has Permission To Use The Command And If It Is In An Approved Channel
# Order of checks: Admin permission, Bypass Role, Channel, Role
def has_perms(setting: str):

    async def has_bypass_role(ctx: commands.Context):
        sql = """SELECT setting_value FROM guild_settings
                WHERE guild_id=$1 AND setting_name='bypass.role'"""
        row = await discordClient.db.fetch(sql, ctx.guild.id)

        if row:
            for i in row[0].split(","):
                i = int(i)
                try:
                    await commands.has_any_role(i).predicate(ctx)
                    return True
                except commands.MissingAnyRole or commands.NoPrivateMessage:
                    pass
            else:
                return False

    async def has_role(setting: str, ctx: commands.Context):

        setting = setting + ".role"
        sql = """SELECT setting_value FROM guild_settings
                WHERE guild_id=$1 AND setting_name=$2;"""
        row = await discordClient.db.fetch(sql, ctx.guild.id, setting)

        if row:
            for i in row[0].split(","):
                i = int(i)
                try:
                    await commands.has_any_role(i).predicate(ctx)
                    return True
                except commands.MissingAnyRole or commands.NoPrivateMessage:
                    pass
            else:
                return False
        else:
            return False

    async def in_channel(setting: str, ctx: commands.Context):
        setting = setting + ".channel"
        sql = """SELECT setting_value FROM guild_settings
                WHERE guild_id=$1 AND setting_name=$2"""
        row = await discordClient.db.fetch(sql, ctx.guild.id, setting)

        if row:
            return str(ctx.channel.id) in row[0].split(",")
        else:
            return False

    async def predicate(ctx: commands.Context):
        try:
            if await commands.has_permissions(administrator=True).predicate(ctx):
                return True
        except commands.MissingPermissions:
            if await has_bypass_role(ctx):
                return True
            elif await has_role(setting, ctx):
                if await in_channel(setting, ctx):
                    return True
                else:
                    return False
            else:
                return False

    return commands.check(predicate)

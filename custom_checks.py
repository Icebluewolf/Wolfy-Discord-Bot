# Custom Checks

import discord
from config import cur
from discord.ext import commands


def allowed_roles(module):
    async def predicate(ctx):
        cur.execute("SELECT " + module + ", bypass_roles_id FROM guild_settings WHERE guild_id=%s",
                    (str(ctx.guild.id),))
        row = cur.fetchall()

        result = row[0][0]
        if row[0][1] is not None:
            result.append(row[0][1])

        author_roles = []
        for i in ctx.author.roles:
            author_roles.append(i.id)

        if result is None and ctx.author.guild_permissions.administrator:
            return True
        for item in result:
            if int(item) in author_roles:
                return True

    return commands.check(predicate)


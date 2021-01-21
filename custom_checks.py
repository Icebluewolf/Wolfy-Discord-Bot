# Custom Checks

import discord
from config import cur
from discord.ext import commands


# Checks If The User Has Permission To Use The Command And If It Is In An Approved Channel
# Any Roles In "bypass_roles_id"(Defaulted to Admins) Bypass *ALL* Restrictions
def allowed_roles(module_roles, module_channels,):
    async def predicate(ctx):
        # Get DB row
        cur.execute("SELECT role_id, bypass_role "
                    "FROM roles WHERE guild_id=%s and (" + module_roles + "=True OR bypass_role=True)",
                    (str(ctx.guild.id),))
        rows = cur.fetchall()

        # print(roles[0])
        # print(roles[0][0])
        approved_roles = []
        bypass_roles = []
        for role in rows:
            # check if the column is not empty
            # if role[0] is True:
            #     approved_roles.append(role[0])
            # if row[0][1] is not None:
            #     channel = row[0][1]
            # else:
            #     channel = []
            if role[1] == 1:
                bypass_roles.append(role[0])
            else:
                approved_roles.append(role[0])

        # get the authors current roles
        author_roles = []
        for i in ctx.author.roles:
            author_roles.append(i.id)

        # If the user is admin let them continue
        if ctx.author.guild_permissions.administrator:
            return True

        # check if the user has a bypass role if so let them continue
        for item in bypass_roles:
            if int(item) in author_roles:
                return True

        # check if the user has a allowed role if so let them continue
        for item in approved_roles:
            if int(item) in author_roles:
                # Check if they are in an approved channel.
                # Call the Channel DB
                cur.execute("SELECT channel_id FROM text_channels WHERE guild_id=%s and " + module_channels + "=True",
                            (str(ctx.guild.id),))
                rows = cur.fetchall()

                # Check if channels is None.
                channel_ids = []
                for channel in rows:
                    channel_ids.append(channel[0])

                # channel_ids = []
                # for i in ctx.guild.text_channels:
                #     channel_ids.append(i.id)

                if str(ctx.channel.id) in channel_ids:
                    return True

    return commands.check(predicate)


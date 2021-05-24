import discord
from discord.ext import commands
from constants import SETTINGS


class GuildSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx, setting=None):
        """
        Allows Server Admins To View The Settings Of The Bot
        Usage: `w!settings [setting]`
        """

        async def get_role_name(column):
            if not column:
                return "Admins Only"
            output = ""
            for role_id in column:
                output = output + ctx.guild.get_role(int(role_id)).name + ", "
            return output

        async def get_channel_name(column):
            if not column:
                return "No Channels"
            output = ""
            for channel_id in column:
                print(channel_id)
                output = output + ctx.guild.get_channel(int(channel_id)).mention + ", "
            return output

        if setting is not None:
            setting = setting.split(".")
            if setting[0] in SETTINGS[1].keys():
                try:
                    if setting[1] in SETTINGS[1][setting[0]][1].keys():
                        msg = f"Description: {SETTINGS[1][setting[0]][1][setting[1]]}\n"
                        await ctx.send(msg)
                        # await ctx.send(msg + '\n'.join(SETTINGS[1][setting[0]][1][setting[1]]))
                    else:
                        await ctx.send(f"I could Not Find The `{setting[1]}` Setting In The `{setting[0]}` Group")
                except IndexError:
                    msg = f"Description: {SETTINGS[1][setting[0]][0]}\n"
                    await ctx.send(msg + '\n'.join(SETTINGS[1][setting[0]][1]))
            else:
                await ctx.send(f"I Could Not Find The `{setting[0]}` Group")
        else:
            msg = f"Description: {SETTINGS[0]}\n"
            msg = msg + '\n'.join(SETTINGS[1])
            await ctx.send(msg)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set(self, ctx, setting, *, value):
        """
        Allows Server Admins To Change The Settings Of The Bot.
        Usage: `w!set <setting> <value>`
        """

        setting = setting.split(".", 1)
        if setting[0] in SETTINGS[1].keys():
            if setting[1] in SETTINGS[1][setting[0]][1]:
                if setting[1] == "role":
                    if ctx.guild.get_role(int(value)) is None:
                        return await ctx.send(f"I Could Not Find A Role With The ID Of `{value}` In This Guild")
                elif setting[1] == "channel":
                    if ctx.guild.get_text_channel(int(value)) is None:
                        return await ctx.send(f"I Could Not Find A Channel With The ID Of `{value}` In This Guild")
                await self.bot.db.execute("""
                INSERT INTO guild_settings (guild_id, setting_name, setting_value)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                setting_value = %s;""",
                                          (ctx.guild.id, f"{setting[0]}.{setting[1]}", value, value))
                await self.bot.conn.commit()
                await ctx.send(f"Changed The `{setting[0]}.{setting[1]}` Setting To \n`{value}`")
            else:
                await ctx.send(f"I Could not Find The `{setting[1]}` Setting In The `{setting[0]}` Group")
        else:
            await ctx.send(f"I could not find the `{setting[0]}` group")


def setup(client):
    client.add_cog(GuildSettings(client))

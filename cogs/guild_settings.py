import discord
from discord.ext import commands
from constants import SETTINGS


class GuildSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    #
    # @staticmethod
    # async def is_channel(ctx: commands.Context, discord_id: str) -> bool:
    #     if ctx.guild.get_channel(int(discord_id)):
    #         return True
    #
    # @staticmethod
    # async def is_role(ctx: commands.Context, discord_id: str) -> bool:
    #     if ctx.guild.get_role(int(discord_id)):
    #         return True
    #
    # @staticmethod
    # async def is_int(value: str) -> bool:
    #     try:
    #         int(value)
    #         return True
    #     except ValueError:
    #         return False

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx, setting=None):
        """
        Allows Server Admins To View The Settings Of The Bot
        Usage: `w!settings [setting]`
        """

        # async def get_role_name(column):
        #     if not column:
        #         return "Admins Only"
        #     output = ""
        #     for role_id in column:
        #         output = output + ctx.guild.get_role(int(role_id)).name + ", "
        #     return output
        #
        # async def get_channel_name(column):
        #     if not column:
        #         return "No Channels"
        #     output = ""
        #     for channel_id in column:
        #         print(channel_id)
        #         output = output + ctx.guild.get_channel(int(channel_id)).mention + ", "
        #     return output

        if setting is not None:
            setting = setting.split(".")
            if setting[0] in SETTINGS.keys():
                try:
                    if setting[1] in SETTINGS[setting[0]].keys():
                        msg = f"Description: {SETTINGS[setting[0]][setting[1]]['description']}\n"
                        await ctx.send(msg)
                        # await ctx.send(msg + '\n'.join(SETTINGS[1][setting[0]][1][setting[1]]))
                    else:
                        await ctx.send(f"I could Not Find The `{setting[1]}` Setting In The `{setting[0]}` Group")
                except IndexError:
                    msg = f"Description: {SETTINGS[setting[0]]['description']}\n"
                    cmds = list(SETTINGS[setting[0]].keys())
                    cmds.remove("description")
                    await ctx.send(msg + '\n'.join(cmds))
            else:
                await ctx.send(f"I Could Not Find The `{setting[0]}` Group")
        else:
            msg = f"Description: {SETTINGS['description']}\n"
            groups = list(SETTINGS.keys())
            groups.remove("description")
            msg = msg + '\n'.join(groups)
            await ctx.send(msg)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set(self, ctx, setting, *, value):
        """
        Allows Server Admins To Change The Settings Of The Bot.
        Usage: `w!set <setting> <value>`
        """

        setting = setting.split(".", 1)
        if setting[0] in SETTINGS.keys():
            if setting[1] in SETTINGS[setting[0]]:
                # setting_type = SETTINGS[setting[0]][setting[1]]['type']
                # if not exec(f"GuildSettings.is_{setting_type}({ctx}, {value})"):
                #     return await ctx.send("That Value Did Not Match The Type Of That Setting")
                value = ascii(value)
                await self.bot.db.execute("""
                INSERT INTO guild_settings (guild_id, setting_name, setting_value)
                VALUES ($1, $2, $3)
                ON DUPLICATE KEY UPDATE
                setting_value = $4;""", ctx.guild.id, f"{setting[0]}.{setting[1]}", value, value)
                await ctx.send(f"Changed The `{setting[0]}.{setting[1]}` Setting To \n`{value}`")
            else:
                await ctx.send(f"I Could not Find The `{setting[1]}` Setting In The `{setting[0]}` Group")
        else:
            await ctx.send(f"I could not find the `{setting[0]}` group")


def setup(client):
    client.add_cog(GuildSettings(client))

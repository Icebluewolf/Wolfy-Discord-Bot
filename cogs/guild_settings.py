import re
import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from constants import SETTINGS

choices = [x for x in SETTINGS.keys() if x != "description"]
for y in SETTINGS.keys():
    if y != "description":
        for x in SETTINGS[y].keys():
            if x != "description":
                choices.append(f"{y}.{x}")


class GuildSettings(discord.Cog):
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

    @slash_command()
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx,
                       setting: Option(str, "The Setting You Want To Learn More About", required=False,
                                       choices=choices)):
        """
        Allows Server Admins To View The Settings Of The Bot
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
                        await ctx.respond(msg)
                        # await ctx.respond(msg + '\n'.join(SETTINGS[1][setting[0]][1][setting[1]]))
                    else:
                        await ctx.respond(f"I could Not Find The `{setting[1]}` Setting In The `{setting[0]}` Group")
                except IndexError:
                    msg = f"Description: {SETTINGS[setting[0]]['description']}\n"
                    cmds = list(SETTINGS[setting[0]].keys())
                    cmds.remove("description")
                    await ctx.respond(msg + '\n'.join(cmds))
            else:
                await ctx.respond(f"I Could Not Find The `{setting[0]}` Group")
        else:
            msg = f"Description: {SETTINGS['description']}\n"
            groups = list(SETTINGS.keys())
            groups.remove("description")
            msg = msg + '\n'.join(groups)
            await ctx.respond(msg)

    @slash_command()
    @commands.has_permissions(administrator=True)
    async def set(self, ctx,
                  setting: Option(str, "The Setting To Change", choices=choices),
                  value: Option(str, "The New Value For The Setting")):
        """
        Allows Server Admins To Change The Settings Of The Bot.
        """

        setting = setting.split(".", 1)
        if setting[0] in SETTINGS.keys():
            try:
                if setting[1] in SETTINGS[setting[0]]:
                    # setting_type = SETTINGS[setting[0]][setting[1]]['type']
                    # if not exec(f"GuildSettings.is_{setting_type}({ctx}, {value})"):
                    #     return await ctx.respond("That Value Did Not Match The Type Of That Setting")
                    value = re.sub("[^0-9]", "", ascii(value))
                    await self.bot.db.execute("""
                    INSERT INTO guild_settings (guild_id, setting_name, setting_value)
                    VALUES ($1, $2, $3)
                    ON CONFLICT ON CONSTRAINT guild_settings_pkey DO UPDATE
                    SET setting_value = $4;""", ctx.guild.id, f"{setting[0]}.{setting[1]}", value, value)
                    await ctx.respond(f"Changed The `{setting[0]}.{setting[1]}` Setting To \n`{value}`")
                else:
                    await ctx.respond(f"I Could not Find The `{setting[1]}` Setting In The `{setting[0]}` Group")
            except IndexError:
                await ctx.respond("Make Sure To Use `/set <setting>.<value>` (Without The `<>`)")
        else:
            await ctx.respond(f"I could not find the `{setting[0]}` group")


def setup(client):
    client.add_cog(GuildSettings(client))

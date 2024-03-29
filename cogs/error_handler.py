import traceback
import discord
from config import discordClient
from discord.ext import commands
from .utility.custom_errors import MissingSetting


class CommandErrorHandler(discord.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.respond(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.respond(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.MissingPermissions):
            await ctx.respond(error)

        elif isinstance(error, MissingSetting):
            await ctx.respond(error)

        else:
            # Send To Bug Report Channel If Main Bot
            if discordClient.user.id == 714954765368295486:
                # All other Errors not returned come here
                await ctx.respond(f"There Was An Error. Join The Support Server For Help: https://discord.gg/f39cJ9D")
                # For Reporting Bugs To The Support Server, By Sending The Traceback
                channel = discordClient.get_channel(933351512665632820)
                if channel is None:
                    channel = await discordClient.fetch_channel(933351512665632820)
                await channel.send(
                    f"""There Was An Error. <@!451848182327148554>\nError: \n```
                    {"".join(traceback.format_exception(type(error), error, error.__traceback__))}```"""
                )
            # Send To User If Test Bot
            else:
                # All other Errors not returned come here. And we can just print the default TraceBack.
                await ctx.respond(f"""Error: \n```
                               {"".join(traceback.format_exception(type(error), error, error.__traceback__))}```""")


def setup(client):
    client.add_cog(CommandErrorHandler(client))


# class InvalidRoleSetting(discord.DiscordException):
#     def __init__(self, ctx: commands.Context, setting):
#         self.embed = discord.Embed(title="Error - InvalidRoleSetting",
#                                    description=f"The `{setting}` is either empty or does not contain a valid role ID",
#                                    color=discord.Colour.red)
#         await ctx.respond(embed=self.embed)

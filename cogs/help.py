import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands, pages
from discord.commands import slash_command, Option


# class CustomHelp(commands.Cog):
#     def get_command_signature(self, command):
#         return f"/{command.qualified_name} {command.signature}"
#
#     @slash_command(name="help", description="Provides Help For All Parts Of The Bot")
#     async def help_command(self, ctx,
#                            cmd: Option(str, required=False, description="What You Want To Know More About",
#                                        default=None, choices=)):

class CustomHelp(commands.HelpCommand):
    def get_command_signature(self, command):
        return f"{self.context.clean_prefix}{command.qualified_name} {command.signature}"

    async def respond_bot_help(self, mapping):
        embed = discord.Embed(title="Help Page For Wolfy", color=12345)
        for cog, cog_commands in mapping.items():
            filtered = await self.filter_commands(cog_commands, sort=True)
            command_sigs = [self.get_command_signature(c) for c in filtered]
            if command_sigs:
                cog_name = getattr(cog, "qualified_name", "Un-Categorized")
                embed.add_field(name=cog_name, value="\n".join(command_sigs), inline=False)

        channel = self.get_destination()
        await channel.respond(embed=embed)

    async def respond_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command))
        embed.add_field(name="Description", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.respond(embed=embed)

    async def respond_group_help(self, group):
        embed = discord.Embed(title=self.get_command_signature(group))
        embed.add_field(name="Description", value=group.help)
        alias = group.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        filtered = await self.filter_commands(group.commands, sort=True)
        command_sigs = [self.get_command_signature(c) for c in filtered]
        if command_sigs:
            embed.add_field(name="Sub-Commands", value="\n".join(command_sigs), inline=False)

        channel = self.get_destination()
        await channel.respond(embed=embed)

    async def respond_error_message(self, error):
        embed = discord.Embed(title="Error", description=error)
        channel = self.get_destination()
        await channel.respond(embed=embed)

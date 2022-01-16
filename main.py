import discord
import os
from config import discordClient
import private
import global_functions
from discord.ext import commands


def main_code():
    @discordClient.event
    async def on_ready():
        # Prints Console Message When Bot Has Finished Turning On.
        print("READY!")
        await discordClient.change_presence(status=discord.Status.online, activity=discord.Game("In The Snow"))

    @commands.is_owner()
    @commands.command(hidden=True)
    async def load(ctx, extension):
        discordClient.load_extension(f"cogs.{extension}")
        await ctx.message.add_reaction("\U00002705")

    @commands.is_owner()
    @commands.command(hidden=True)
    async def unload(ctx, extension):
        discordClient.unload_extension(f"cogs.{extension}")
        await ctx.message.add_reaction("\U00002705")

    @commands.is_owner()
    @commands.command(hidden=True)
    async def reload(ctx, extension):
        discordClient.unload_extension(f"cogs.{extension}")
        discordClient.load_extension(f"cogs.{extension}")
        await ctx.message.add_reaction("\U00002705")

    @discordClient.command()
    async def ping(ctx):
        # Simple Command That Sends The Bots Ping/Latency
        """
        Pings The Bots Server
        """

        await ctx.message.delete()
        await ctx.send(embed=await global_functions.create_embed(title="",
                                                                 description=
                                                                 f"Pong :ping_pong:\nPing : `{discordClient.latency}`"),
                       delete_after=30)

    class Counter(discord.ui.View):

        @discord.ui.button(label='0', style=discord.ButtonStyle.red)
        async def count(self, button: discord.ui.Button, interaction: discord.Interaction):
            number = int(button.label) if button.label else 0
            if number + 1 >= 5:
                button.style = discord.ButtonStyle.green
                button.disabled = True
            button.label = str(number + 1)

            await interaction.response.edit_message(view=self)

    class Dropdown(discord.ui.Select):
        def __init__(self):


            options = [
                discord.SelectOption(label='Red', description='Your favourite colour is red', emoji='🟥'),
                discord.SelectOption(label='Green', description='Your favourite colour is green', emoji='🟩'),
                discord.SelectOption(label='Blue', description='Your favourite colour is blue', emoji='🟦')
            ]

            super().__init__(placeholder='Choose your favourite colour...', min_values=1, max_values=2, options=options)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.send_message(f'Your favourite colour is {self.values[0]}')

    class DropdownView(discord.ui.View):
        def __init__(self):
            super().__init__()

            # Adds the dropdown to our view object.
            self.add_item(Dropdown())

    @discordClient.command()
    async def count(ctx: commands.Context):
        await ctx.send("Press!", view=Counter())
        await ctx.send("Dropdown!", view=DropdownView())

    @discordClient.command()
    async def test(ctx):
        tlist = [1, 2]
        slist = tlist[4]
        await ctx.send(slist)

    @discordClient.event
    async def on_guild_join(guild, bot_instance):
        # Sends a join message when the bot joins a server
        bot = guild.me
        for channel in guild.text_channels:
            bot_perms = bot.permissions_in(channel)
            if bot_perms.send_messages:
                await channel.send(f"Thanks for inviting me members of {guild}. "
                                   f"To get started an admin can run w!settings")
                break
        #
        # # Add Row In guild_settings
        # sql = "INSERT INTO guild_settings (guild_id) " \
        #       "VALUES (%s) " \
        #       "ON DUPLICATE KEY UPDATE guild_id = (%s);"
        # bot_instance.db.execute(sql, (guild.id, guild.id))

    @discordClient.event
    async def on_member_join(member, bot):
        # Sets Up The Users Database User Info When A User Join A Server
        sql = "SELECT * FROM user_data WHERE discord_user_id=$1 AND guild_id=$2"
        row = bot.db.fetch(sql, member.id, member.guild.id)
        if row:
            return
        else:
            await global_functions.add_user_db_row(member, bot)

    # Run The Bot And Load Cogs
    COGS = ["cogs.guild_settings", "cogs.timers", "cogs.reaction_roles", "cogs.poll", "cogs.moderation",
            "cogs.error_handler"]
    for cog in COGS:
        discordClient.load_extension(cog)

    discordClient.load_extension('jishaku')
    discordClient.run(private.clientSecret)


if __name__ == "__main__":
    main_code()

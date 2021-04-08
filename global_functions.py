import discord
# from config import cur, DB_conn


async def add_user_db_row(member, bot):
    await bot.db.execute(
                "INSERT INTO user_data (discord_user, discord_user_id, whitelist, guild_id) "
                "VALUES ('{}', {}, True, {});".format(member.name + "#" + member.discriminator,
                                                      member.id,
                                                      member.guild.id))
    await bot.db.commit()


async def create_embed(title, description, color=0x08D4D0):
    if title == "error":
        title = "There Was An Error :/"
        color = 0xE90000
    elif title == "fail":
        title = "You Cant Do That :("
        color = 0xF0FF00
    elif title == "invalid":
        title = "I Cant Do That O_o"
        color = 0xAE23F0
    elif title == "success":
        title = "Success! :)"
        color = 0x4BF615
    embed = discord.Embed(title=title,
                          description=description,
                          type="rich",
                          color=color, )
    return embed

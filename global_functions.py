from config import cur, DB_conn


async def add_user_db_row(member):
    cur.execute(
                "INSERT INTO user_data (discord_user, discord_user_id, whitelist, guild_id) "
                "VALUES ('{}', {}, True, {});".format(member.name + "#" + member.discriminator,
                                                      member.id,
                                                      member.guild.id))
    DB_conn.commit()

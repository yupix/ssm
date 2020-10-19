import mysql
from discord.ext import commands

from main import embed_send, db_blogwar_database, db_password, db_user, db_port, db_host, db_search

bgw_mydb = mysql.connector.connect(
    host=f'{db_host}',
    port=f'{db_port}',
    user=f'{db_user}',
    password=f'{db_password}',
    database=f'{db_blogwar_database}'
)

bgw_mycursor = bgw_mydb.cursor()


async def bgw_db_search(table_name, table_column, where_condition):
    bgw_mycursor.execute(
        f'SELECT {table_name} FROM {table_column} WHERE {where_condition} LIMIT 1')
    myresult = bgw_mycursor.fetchall()
    return myresult


class Basic_BgwCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bgw(self, ctx):
        print('bgw')


def setup(bot):
    bot.add_cog(Basic_BgwCog(bot))

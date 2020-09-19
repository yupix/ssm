import os
import urllib

import discord
import mysql.connector
import traceback
import configparser

from discord.ext import commands
from discord.ext.commands import CommandNotFound
from halo import Halo

config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')

bot_user = config_ini['DEFAULT']['User']
bot_prefix = config_ini['DEFAULT']['Prefix']
bot_token = config_ini['DEFAULT']['Token']

db_user = config_ini['DATABASE']['User']
db_port = config_ini['DATABASE']['Port']
db_host = config_ini['DATABASE']['Host']
db_password = config_ini['DATABASE']['Password']
db_database = config_ini['DATABASE']['Database']

custom_blogrole = config_ini['CUSTOM']['Blogrole']
mydb = mysql.connector.connect(
    host=f'{db_host}',
    port=f'{db_port}',
    user=f'{db_user}',
    password=f'{db_password}',
    database=f'{db_database}'
)

mycursor = mydb.cursor()

INITIAL_EXTENSIONS = [
    'cogs.testcog',
    'cogs.blogcog',
    'cogs.basiccog',
    'cogs.blocklistcog',
    'cogs.modpackcog'
]

async def check_url(url):
    try:
        f = urllib.request.urlopen(url)
        print('OK:', url)
        f.close()
    except urllib.request.HTTPError:
        print('Not found:', url)

async def embed_send(ctx, bot, type, title, subtitle):
    if type == 0:  # 成功時
        embed_color = 0x8bc34a
    elif type == 1:  # エラー発生時
        embed_color = 0xd32f2f
    print(f'{type}, {title}, {subtitle}')
    embed = discord.Embed(title=f'{title}', description=f'{subtitle}', color=embed_color)
    m = await bot.get_channel(ctx.message.channel.id).send(embed=embed)
    return m

async def db_update(table_name, table_column, val):
    sql = f'UPDATE {table_name} SET {table_column}'
    mycursor.execute(sql, val)
    mydb.commit()


async def db_search(table_name, table_column, where_condition):
    mycursor.execute(
        f'SELECT {table_name} FROM {table_column} WHERE {where_condition} LIMIT 1')
    myresult = mycursor.fetchall()
    return myresult


async def db_reformat(myresult, type):
    for x in myresult:
        reformat = "".join(map(str, x))
    if type == 0:
        return myresult
    elif type == 1:
        return str(reformat)
    elif type == 2:
        return int(reformat)
    elif type == 3:
        return float(reformat)
    elif type == 4:
        return list(reformat)

async def db_delete(table_column, where_condition, adr):
    sql = f'DELETE FROM {table_column} WHERE {where_condition}'
    adr = (adr,)
    mycursor.execute(sql, adr)

    mydb.commit()


def check_database():  # 起動時に一度実行jsonがあるか確認ないなら作成する関数
    if os.path.exists('./tmp/dummy'):
        print('\r' + f'[main/INFO] tmpのチェック に成功')
        mycursor.execute('USE discord_bot')
    else:
        mycursor.execute('DROP DATABASE discord_bot')
        mycursor.execute('CREATE DATABASE discord_bot')
        mycursor.execute('USE discord_bot')
        # discord_main_blog を作る
        mycursor.execute(
            'CREATE TABLE discord_blog_main_info (server_id VARCHAR(255), category_id VARCHAR(255), '
            'blog_reply_channel VARCHAR(255), blog_reply_webhook_url VARCHAR(255), role VARCHAR(255))')

        # discord_blog_sub_info を作る
        mycursor.execute(
            'CREATE TABLE discord_blog_sub_info (channel_id VARCHAR(255), user_id VARCHAR(255),  embed_color VARCHAR('
            '255), number_of_posts VARCHAR(255))')

        # discord_blog_xp を作る
        mycursor.execute(
            'CREATE TABLE discord_blog_xp (channel_id VARCHAR(255), xp VARCHAR(255), '
            'level VARCHAR(255), saved_levelup_xp VARCHAR(255))')

        # discord_blog_user_info を作る
        mycursor.execute(
            'CREATE TABLE discord_blog_user_info (channel_id VARCHAR(255), last_logind VARCHAR(255), number_logins '
            'VARCHAR(255), total_login VARCHAR(255))')

        # discord_main_block_list を作る
        mycursor.execute(
            'CREATE TABLE discord_main_block_list (server_id VARCHAR(255), role VARCHAR(255), cooperation VARCHAR(255))')

        # discord_sub_block_list を作る
        mycursor.execute(
            'CREATE TABLE discord_sub_block_list (server_id VARCHAR(255), user_id VARCHAR(255), count VARCHAR(255))')

        # discord_modpack_main_info を作る
        mycursor.execute(
            'CREATE TABLE discord_modpack_main_info (id int auto_increment, author_id VARCHAR(255), pack_name VARCHAR(255), pack_mc_version VARCHAR(255), index(id))')

        # discord_modpack_sub_info を作る
        mycursor.execute(
            'CREATE TABLE discord_modpack_sub_info (id int auto_increment, pack_description VARCHAR(255), pack_tags VARCHAR(255), index(id))')

        with open('./tmp/dummy', mode='x') as f:
            f.write('')


class ssm(commands.Bot):

    def __init__(self, command_prefix):
        super().__init__(command_prefix)

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        check_database()
        # discord_reaction_data を消す
        sql = "DROP TABLE IF EXISTS discord_reaction"

        mycursor.execute(sql)

        # discord_reaction_data を作る
        mycursor.execute(
            'CREATE TABLE discord_reaction (channel_id VARCHAR(255), message_id VARCHAR(255), user_id VARCHAR(255), command VARCHAR(255), mode VARCHAR(255), original_message_id VARCHAR(255))')
        spinner.stop()
        print('--------------------------------')
        print(self.user.name)
        print(self.user.id)
        print('--------------------------------')

    async def on_message(self, ctx):
        print(f'[[ 発言 ]] {ctx.guild.name}=> {ctx.channel.name}=> {ctx.author.name}: {ctx.content}')
        await bot.process_commands(ctx)

    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            await ctx.send('存在しないコマンドです')
            return
        else:
            embed = discord.Embed(title='エラーレポート', description='', color=0xd32f2f)
            embed.add_field(name='エラー発生サーバーID', value=ctx.guild.id, inline=True)
            embed.add_field(name='エラー発生ユーザーID', value=ctx.author.id, inline=True)
            embed.add_field(name='エラー発生コマンド', value=ctx.message.content, inline=True)
            embed.add_field(name='エラー内容', value=error, inline=True)
            m = await bot.get_channel(ctx.message.channel.id).send(embed=embed)
            await ctx.send(f'申し訳ありません、内部エラーが発生しました。コードと一緒にエラー報告をしていただけると助かります：{m.id}')


if __name__ == '__main__':
    spinner = Halo(text='Loading Now',
                   spinner={
                       'interval': 300,
                       'frames': ['-', '+', 'o', '+', '-']
                   })
    spinner.start()

    bot = ssm(command_prefix=f'{bot_prefix}')
    bot.run(f'{bot_token}')

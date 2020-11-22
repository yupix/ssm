import json
import os
import urllib

import coloredlogs
import discord
import mysql.connector
import traceback
import configparser

from discord.ext import commands
from discord.ext.commands import CommandNotFound
from halo import Halo
from logging import getLogger, StreamHandler, DEBUG, Formatter, addLevelName

config_ini = configparser.ConfigParser(os.environ)
config_ini.read('config.ini', encoding='utf-8')

bot_user = config_ini['DEFAULT']['User']
bot_prefix = config_ini['DEFAULT']['Prefix']
bot_token = config_ini['DEFAULT']['Token']

db_user = config_ini['DATABASE']['User']
db_port = config_ini['DATABASE']['Port']
db_host = config_ini['DATABASE']['Host']
db_password = config_ini['DATABASE']['Password']
db_default_database = config_ini['DATABASE']['Default_Database']

reset_status = config_ini['RESET']['Status']

custom_blogrole = config_ini['CUSTOM']['Blogrole']

Dic_Path = config_ini['JTALK']['Dic_Path']
Voice_Path = config_ini['JTALK']['Voice_Path']
Jtalk_Bin_Path = config_ini['JTALK']['Jtalk_Bin_Path']
Output_wav_name = config_ini['JTALK']['Output_wav_name']
Spped = config_ini['JTALK']['Spped']

# --------------------------------
# 1.loggerの設定
# --------------------------------
# loggerオブジェクトの宣言
logger = getLogger(__name__)

# loggerのログレベル設定(ハンドラに渡すエラーメッセージのレベル)
logger.setLevel(DEBUG)

# --------------------------------
# 2.handlerの設定
# --------------------------------
# handlerの生成
stream_handler = StreamHandler()

# handlerのログレベル設定(ハンドラが出力するエラーメッセージのレベル)
stream_handler.setLevel(DEBUG)

# --------------------------------
# 3.loggerにhandlerをセット
# --------------------------------
logger.addHandler(stream_handler)
logger.propagate = False

coloredlogs.CAN_USE_BOLD_FONT = True
coloredlogs.DEFAULT_FIELD_STYLES = {'asctime': {'color': 'green'},
                                    'hostname': {'color': 'magenta'},
                                    'levelname': {'color': 'black', 'bold': True},
                                    'name': {'color': 'blue'},
                                    'programname': {'color': 'cyan'}
                                    }
coloredlogs.DEFAULT_LEVEL_STYLES = {'critical': {'color': 'red', 'bold': True},
                                    'error': {'color': 'red'},
                                    'warning': {'color': 'yellow'},
                                    'notice': {'color': 'magenta'},
                                    'info': {'color': 'green'},
                                    'debug': {},
                                    'spam': {'color': 'green', 'faint': True},
                                    'success': {'color': 'green', 'bold': True},
                                    'verbose': {'color': 'blue'}
                                    }

coloredlogs.install(level='DEBUG', logger=logger, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

# SUCCESSを追加
logger.SUCCESS = 25 # WARNINGとINFOの間
addLevelName(logger.SUCCESS, 'SUCCESS')
setattr(logger, 'success', lambda message, *args: logger._log(logger.SUCCESS, message, args))


mydb = mysql.connector.connect(
    host=f'{db_host}',
    port=f'{db_port}',
    user=f'{db_user}',
    password=f'{db_password}',
    database=f'{db_default_database}'
)

mycursor = mydb.cursor()

INITIAL_EXTENSIONS = [
    'cogs.testcog',
    'cogs.blogcog',
    'cogs.basiccog',
    'cogs.blocklistcog',
    'cogs.modpackcog',
    'cogs.hostlabcog',
    'cogs.read'
]


async def retry_db_connection():
    mydb = mysql.connector.connect(
        host=f'{db_host}',
        port=f'{db_port}',
        user=f'{db_user}',
        password=f'{db_password}',
        database=f'{db_default_database}'
    )
    global mycursor
    mycursor = mydb.cursor()


async def check_url(url):
    try:
        f = urllib.request.urlopen(url)
        print('OK:', url)
        f.close()
        return 0
    except urllib.request.HTTPError:
        print('Not found:', url)
        return 1


async def embed_send(ctx, bot, type, title, subtitle):
    if type == 0:  # 成功時
        embed_color = 0x8bc34a
    elif type == 1:  # エラー発生時
        embed_color = 0xd32f2f
    logger.debug(f'{type}, {title}, {subtitle}')
    embed = discord.Embed(title=f'{title}', description=f'{subtitle}', color=embed_color)
    m = await bot.get_channel(ctx.message.channel.id).send(embed=embed)
    return m


async def db_update(table_name, table_column, val):
    sql = f'UPDATE {table_name} SET {table_column}'
    mycursor.execute(sql, val)
    mydb.commit()


async def db_insert(sql, val):
    mycursor.execute(sql, val)
    mydb.commit()

async def db_get_auto_increment():
    mycursor.execute(
        f'SELECT last_insert_id();')
    myresult = mycursor.fetchall()
    result = await db_reformat(myresult, 2)
    return result


async def db_search(table_name, table_column, where_condition, *args):
    if not args:
        mycursor.execute(
            f'SELECT {table_name} FROM {table_column} WHERE {where_condition}')
        myresult = mycursor.fetchall()
        return myresult
    else:
        mycursor.execute(
            f'SELECT {args}')
        myresult = mycursor.fetchall()
        return myresult


async def db_reformat(myresult, type):
    if len(myresult) > 0 :
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
    else:
        return None


async def db_delete(table_column, where_condition, adr):
    sql = f'DELETE FROM {table_column} WHERE {where_condition}'
    adr = (adr,)
    mycursor.execute(sql, adr)

    mydb.commit()


def json_load(path):
    json_open = open(f'{path}', 'r')
    json_load = json.load(json_open)
    return json_load

def create_default_table():
    mycursor.execute('USE default_discord')

    # discord_reaction_data を作る
    database_table_list_load = json_load("./template/database_table.json")

    for x in database_table_list_load.keys():
        if f'{x}' == 'delete':
            for n in database_table_list_load[x]['table']:
                get_table_name = database_table_list_load[f'{x}']['table'][f'{n}']
                sql = (f'DROP TABLE IF EXISTS {get_table_name}')
                mycursor.execute(sql)
        elif f'{x}' == 'create':
            for n in database_table_list_load[f'{x}']['table']:
                set_column = ""
                for i in database_table_list_load[f'{x}']['table'][f'{n}']['column']:
                    get_column = database_table_list_load[f'{x}']['table'][f'{n}']['column'][f'{i}']
                    set_column += get_column + ', '
                mycursor.execute(
                    f'CREATE TABLE IF NOT EXISTS {n} ({set_column[:-2]})')


def check_database():
    if os.path.exists('./tmp/dummy'):
        logger.success('tmpのチェック に成功')
    else:
        mycursor.execute('DROP DATABASE IF EXISTS default_discord')
        mycursor.execute('CREATE DATABASE default_discord')

        mycursor.execute('DROP DATABASE IF EXISTS discord_blogwar')
        mycursor.execute('CREATE DATABASE discord_blogwar')

        with open('./tmp/dummy', mode='x') as f:
            f.write('')

    create_default_table()

class ssm(commands.Bot):

    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, help_command=None, description=None, intents=intents)

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        check_database()
        spinner.stop()
        print('--------------------------------')
        print(self.user.name)
        print(self.user.id)
        print('--------------------------------')

    async def on_message(self, ctx):
        """利用規約同意のデータが追加されたあとも認識しないため一時的にコメントアウト
        if ctx.author.bot:
            return
        command_list_load = json_load("./template/command_list.json")

        message_content = ctx.content.split()
        for x in command_list_load['command']:
            command_name = command_list_load['command'][x]
            if message_content[0] == bot_prefix + command_name:
                check_command = 'yes'


        mycursor.execute(
            f'SELECT consent_status FROM server_main_info WHERE server_id = {ctx.guild.id} LIMIT 1')
        check_consent_status = mycursor.fetchall()

        print(check_consent_status)
        if not check_consent_status:
            if 'check_command' in locals():
                embed = discord.Embed(
                    title='エラー', description=f'利用規約に同意していません！以下のコマンドで利用規約に同意してください\n```{bot_prefix}agree```', color=0xd32f2f)

                await ctx.channel.send(embed=embed)
                return 1

        """
        logger.info(f'{ctx.guild.name}=> {ctx.channel.name}=> {ctx.author.name}: {ctx.content}')
        #print(f'[[ 発言 ]] {ctx.guild.name}=> {ctx.channel.name}=> {ctx.author.name}: {ctx.content}')
        await bot.process_commands(ctx)

"""    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            await ctx.send('存在しないコマンドです')
            return 1
        else:
            print(error)
            if str(error) in 'Command raised an exception: OperationalError: 2055:':
                await retry_db_connection()
                await ctx.send(f'申し訳ありません、データベースエラーが発生しました。エラーが発生したことにより自動的に修正された可能性があります！再度実行してエラーが出るようであれば報告してください。')
            else:
                embed = discord.Embed(title='エラーレポート', description='', color=0xd32f2f)
                embed.add_field(name='エラー発生サーバーID', value=ctx.guild.id, inline=True)
                embed.add_field(name='エラー発生ユーザーID', value=ctx.author.id, inline=True)
                embed.add_field(name='エラー発生コマンド', value=ctx.message.content, inline=True)
                embed.add_field(name='エラー内容', value=error, inline=True)
                m = await bot.get_channel(ctx.message.channel.id).send(embed=embed)
                await ctx.send(f'申し訳ありません、内部エラーが発生しました。コードと一緒にエラー報告をしていただけると助かります：{m.id}')
"""

if __name__ == '__main__':
    spinner = Halo(text='Loading Now',
                   spinner={
                       'interval': 300,
                       'frames': ['-', '+', 'o', '+', '-']
                   })
    spinner.start()

    intents = discord.Intents.all()

    bot = ssm(command_prefix=f'{bot_prefix}', intents=intents)
    bot.run(f'{bot_token}')

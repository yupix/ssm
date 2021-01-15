import json
import os
import time
import urllib

import discord
import mysql.connector
import traceback
import configparser
import typing

from discord.ext import commands
from discord.ext.commands import CommandNotFound
from halo import Halo
from logging import getLogger, StreamHandler, DEBUG, Formatter, addLevelName

from sqlalchemy.exc import IntegrityError

from modules.create_logger import easy_logger
from settings import session
from sql.models.user import *

config_ini = configparser.ConfigParser(os.environ)
config_ini.read('./config.ini', encoding='utf-8')
config = configparser.ConfigParser()
config.read('./config.ini', encoding='utf-8')

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

logger = easy_logger.create(logger)

INITIAL_EXTENSIONS = [
    'cogs.testcog',
    'cogs.note',
]


def add_list(hit, key, args_list):
    if hit is not None:
        args_list[f'{hit}'] = key
        hit = None
        return hit, args_list
    else:
        hit = key
        return hit, args_list


def check_args(argument):
    split_argument = argument.lower().split(' ')
    hit = None
    args_list = {}
    for i in split_argument:
        if i == '--type' or i == '--test2' or i == '--max' or i == '-c' or hit is not None:
            hit, args_list = add_list(hit, i, args_list)

    else:
        logger.debug(hit)
        if hit is not None:
            return '1', f'{i}には引数が必要です'
        else:
            print(args_list)
            return args_list


async def check_variable(variable, error_message: typing.Optional[str] = None, ctx=None):
    if variable:
        return 0
    else:
        if error_message is not None:
            # await ctx.send(f'{error_message}')
            logger.error('文字列が空です')
        return 1


async def check_url(url):
    try:
        f = urllib.request.urlopen(url)
        print('OK:', url)
        f.close()
        return 0
    except urllib.request.HTTPError:
        print('Not found:', url)
        return 1


async def embed_send(ctx, bot, embed_type, title, subtitle, color=None):
    if color is None:
        if embed_type == 0:  # 成功時
            embed_color = 0x8bc34a
        elif embed_type == 1:  # エラー発生時
            embed_color = 0xd32f2f
    else:
        embed_color = color
    logger.debug(f'{embed_type}, {title}, {subtitle}')
    embed = discord.Embed(title=f'{title}', description=f'{subtitle}', color=embed_color)
    m = await bot.get_channel(ctx.message.channel.id).send(embed=embed)
    return m


async def db_commit(content, autoincrement=None):
    session.add(content)
    try:
        session.commit()
        if autoincrement is None:
            result = 'Success'
        elif autoincrement is True:
            result = content.id

    except IntegrityError as e:
        session.rollback()
        result = 'IntegrityError'
    finally:
        session.close()
    return result




def json_load(path):
    json_open = open(f'{path}', 'r')
    json_load = json.load(json_open)
    return json_load


class ssm(commands.Bot):

    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, help_command=None, description=None, intents=intents)

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        spinner.stop()
        print('--------------------------------')
        print(self.user.name)
        print(self.user.id)
        print('--------------------------------')

    async def on_message(self, ctx):
        logger.info(f'{ctx.guild.name}=> {ctx.channel.name}=> {ctx.author.name}: {ctx.content}')
        # print(f'[[ 発言 ]] {ctx.guild.name}=> {ctx.channel.name}=> {ctx.author.name}: {ctx.content}')
        await bot.process_commands(ctx)


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

import configparser
import json
import os
import traceback
import typing
import urllib
from distutils.util import strtobool
from logging import getLogger

import discord
from discord.ext import commands
from googletrans import Translator
from halo import Halo
from sqlalchemy.exc import IntegrityError

from modules.create_logger import easy_logger
from settings import session

config_ini = configparser.ConfigParser(os.environ)
config_ini.read('./config.ini', encoding='utf-8')
config = configparser.ConfigParser()
config.read('./config.ini', encoding='utf-8')

bot_user = config_ini['DEFAULT']['User']
bot_prefix = config_ini['DEFAULT']['Prefix']
bot_token = config_ini['DEFAULT']['Token']
reset_status = config_ini['RESET']['Status']

custom_blogrole = config_ini['CUSTOM']['Blogrole']

Dic_Path = config_ini['JTALK']['Dic_Path']
Voice_Path = config_ini['JTALK']['Voice_Path']
Jtalk_Bin_Path = config_ini['JTALK']['Jtalk_Bin_Path']
Output_wav_name = config_ini['JTALK']['Output_wav_name']
Spped = config_ini['JTALK']['Spped']
show_bot_chat_log = config_ini['OPTIONS']['show_bot_chat_log']

# --------------------------------
# 1.loggerの設定
# --------------------------------
# loggerオブジェクトの宣言
logger = getLogger(__name__)

logger = easy_logger.create(logger)

INITIAL_EXTENSIONS = [
    'cogs.testcog',
    'cogs.note',
    'cogs.blocklist',
    'cogs.warframe',
    'cogs.pso2',
    'cogs.blog',
]

async def none_check_invoked_subcommand(ctx, error_message):
    if ctx.invoked_subcommand is None:
        await ctx.send('このコマンドには引数が必要です')


def translator(content):
    tr = Translator()
    result = tr.translate(text=f"{content}", src="en", dest="ja").text

    return result


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


async def db_commit(content, autoincrement=None, commit_type='insert'):
    logger.debug('commit')
    if commit_type == 'insert':
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
        if bool(strtobool(show_bot_chat_log)) is False and ctx.author.bot is True:
            return
        logger.info(f'{ctx.guild.name}=> {ctx.channel.name}=> {ctx.author.name}: {ctx.content}')
        await bot.process_commands(ctx)  # コマンド動作用


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

import asyncio
import json
import os
import re
import traceback
import typing
import urllib
import configparser
import discord
import requests as requests

from distutils.util import strtobool
from discord.ext import commands, tasks
from fastapi import FastAPI
from fastapi_versioning import VersionedFastAPI
from googletrans import Translator
from uvicorn import Config, Server
from discord_slash import SlashCommand, SlashContext

from ssm import session, AutoMigrate
from ssm.base import db_manager, logger, spinner
from ssm.modules.voice_generator import create_wave
from ssm.routers import v1
from ssm.sql.models.eew import Eew, EewChannel
from ssm.sql.models.WarframeFissure import WarframeFissuresId, WarframeFissuresDetail, WarframeFissuresMessage, WarframeFissuresChannel
from ssm.sql.models.api import ApiRequests, ApiDetail

config_ini = configparser.ConfigParser(os.environ)
config_ini.read('./config.ini', encoding='utf-8')
config = configparser.ConfigParser()
config.read('./config.ini', encoding='utf-8')

bot_user = config_ini['DEFAULT']['User']
bot_prefix = config_ini['DEFAULT']['Prefix']
bot_token = config_ini['DEFAULT']['Token']
reset_status = config_ini['RESET']['Status']

custom_blogrole = config_ini['CUSTOM']['Blogrole']
use_api = config_ini['API']['use']
use_eew = config_ini['EEW']['use']

Dic_Path = config_ini['JTALK']['Dic_Path']
Voice_Path = config_ini['JTALK']['Voice_Path']
Jtalk_Bin_Path = config_ini['JTALK']['Jtalk_Bin_Path']
Output_wav_name = config_ini['JTALK']['Output_wav_name']
read_aloud = config_ini['JTALK']['read_aloud']
Speed = config_ini['JTALK']['Speed']
show_bot_chat_log = config_ini['OPTIONS']['show_bot_chat_log']

app = FastAPI(title=f'{bot_user} API')
app.include_router(v1.servers.router)
app = VersionedFastAPI(app, version_format='{major}', prefix_format='/v{major}')

INITIAL_EXTENSIONS = [
    'ssm.cogs.testcog',
    'ssm.cogs.note',
    'ssm.cogs.blocklist',
    'ssm.cogs.warframe',
    'ssm.cogs.pso2',
    'ssm.cogs.blog',
    'ssm.cogs.read',
    'ssm.cogs.basic',
    'ssm.cogs.eew',
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
        if i == '--type' or i == '--test2' or i == '--max' or i == '-c' or i == '--register' or i == '--translate' or hit is not None:
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


async def embed_send(ctx, use_bot, embed_type: int, title: str, subtitle: str, color=None) -> discord.Message:
    if color is None:
        if embed_type == 0:  # 成功時
            embed_color = 0x8bc34a
        elif embed_type == 1:  # エラー発生時
            embed_color = 0xd32f2f
        else:
            embed_color = 0xb39ddb
    else:
        embed_color = color
    logger.debug(f'{embed_type}, {title}, {subtitle}')
    embed = discord.Embed(title=f'{title}', description=f'{subtitle}', color=embed_color)
    m = await use_bot.get_channel(ctx.message.channel.id).send(embed=embed)
    return m


def json_load(path):
    json_open = open(f'{path}', 'r')
    json_load = json.load(json_open)
    return json_load


@tasks.loop(seconds=2)
async def api_request():
    check_requests = session.query(ApiRequests).all()
    for request in check_requests:
        print(request.request_content)
        if request.type == 'server_info':
            if request.request_content is None:
                content = {
                    "result": {
                        "type": "failed",
                        "text": "invalid server id"
                    }
                }
            else:
                guild = bot.get_guild(request.request_content['server_id'])
                if guild is None:
                    content = {
                        "result": {
                            "type": "failed",
                            "text": "invalid server id"
                        }
                    }
                else:
                    content = {
                        "result": {
                            "type": "successful"
                        },
                        "body": {
                            "icon_url": f"{guild.icon_url}",
                            "name": f"{guild.name}"
                        }
                    }
            await db_manager.commit(ApiDetail(request_id=request.request_id, content=content))
            await db_manager.commit(session.query(ApiRequests).filter(ApiRequests.request_id == request.request_id).delete(), commit_type='delete')
        if request.request_content is not None:
            print(request.request_content['server_id'])


@tasks.loop(seconds=1)
async def bot_eew_loop():
    from ssm.cogs.eew import EewSendChannel
    url = "https://dev.narikakun.net/webapi/earthquake/post_data.json"
    try:
        result = requests.get(url).json()
    except json.decoder.JSONDecodeError:
        logger.error('eewの情報取得にてエラーが発生しました: コンテンツタイプがjsonではありません')
        return
    logger.debug(result)
    event_id = result['Head']['EventID']
    search_event_id = session.query(Eew).filter(Eew.event_id == event_id).first()
    if search_event_id is None:
        await db_manager.commit(Eew(event_id=event_id))
        eew_manager = EewSendChannel(bot)
        image_url = await eew_manager.get_nhk_image(result['Body']['Earthquake']['OriginTime'])
        search_eew_channel_list = session.query(EewChannel)
        for channel in search_eew_channel_list:
            logger.debug(f'{channel.channel_id}にEew情報を送信します')
            asyncio.ensure_future(eew_manager.main_title_send(channel, result, image_url))


@tasks.loop(seconds=60)
async def loop_bot_task():
    from ssm.cogs.warframe import get_warframe_fissures_api, fissure_tier_conversion, warframe_fissures_embed, mission_eta_conversion

    async def fissure_check():
        for fissure in session.query(WarframeFissuresDetail).order_by(WarframeFissuresDetail.tier):
            if message.detail_id == fissure.id:
                return True, fissure
            else:
                message_search_result = False
        return message_search_result, fissure

    # APIから情報を取得
    fissure_list = get_warframe_fissures_api()
    if fissure_list is None:  # Json形式ではなかった場合用
        return
    for warframe_fissure_id in session.query(WarframeFissuresId).all():
        for fissures in fissure_list:
            search_warframe_fissure_detail = session.query(WarframeFissuresDetail).filter(WarframeFissuresDetail.api_id == f'{warframe_fissure_id.api_id}').first()
            if warframe_fissure_id.api_id != fissures[5]:
                await db_manager.commit(setattr(search_warframe_fissure_detail, 'status', 'True'), commit_type='update', show_commit_log=False)
            else:
                await db_manager.commit(setattr(search_warframe_fissure_detail, 'status', 'False'), commit_type='update', show_commit_log=False)
                break

    # API側で期限切れになっている亀裂がないかを確認
    for i in fissure_list:
        if i[6] is not True:
            check_warframe_fissure_detail = session.query(WarframeFissuresDetail).filter(WarframeFissuresDetail.api_id == f'{i[5]}').first()
            if not check_warframe_fissure_detail or check_warframe_fissure_detail.api_id != f'{i[5]}':
                await db_manager.commit(WarframeFissuresId(api_id=f'{i[5]}'), show_commit_log=False)
                star_name = str(re.findall("(?<=\().+?(?=\))", i[0])).replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace('\'', '')
                await db_manager.commit(
                    WarframeFissuresDetail(api_id=f'{i[5]}', node=f'{i[0]}', enemy=f'{i[2]}', type=f'{i[1]}', tier=f'{i[3]}', tier_original=f'{fissure_tier_conversion(i[3])}', star_name=star_name,
                                           eta=f'{i[4]}', status=f'{i[6]}'), show_commit_log=False)
            else:
                await db_manager.commit(setattr(check_warframe_fissure_detail, 'eta', f'{i[4]}'), commit_type='update', show_commit_log=False)
                await db_manager.commit(setattr(check_warframe_fissure_detail, 'status', f'{i[6]}'), commit_type='update', show_commit_log=False)

    # 新しい亀裂が登録されてるチャンネルに送信されてない場合は送信
    for fissure_id in session.query(WarframeFissuresDetail).order_by(WarframeFissuresDetail.tier):
        check_already_fissure_message = session.query(WarframeFissuresMessage).filter(WarframeFissuresMessage.detail_id == fissure_id.id).first()
        if not check_already_fissure_message:
            for fissure_channel in session.query(WarframeFissuresChannel).all():
                channel = bot.get_channel(int(fissure_channel.channel_id))
                embed = warframe_fissures_embed(fissure_id.node, fissure_id.type, fissure_id.enemy, fissure_tier_conversion(fissure_id.tier), mission_eta_conversion(fissure_id.eta))
                send_embed = await channel.send(embed=embed)
                await db_manager.commit(WarframeFissuresMessage(detail_id=fissure_id.id, message_id=send_embed.id, channel_id=send_embed.channel.id), show_commit_log=False)
                break
    for message in session.query(WarframeFissuresMessage).order_by(WarframeFissuresMessage.id):
        message_search_result, fissure = await fissure_check()
        channel = bot.get_channel(int(message.channel_id))
        get_message = await channel.fetch_message(int(message.message_id))
        if bool(strtobool(fissure.status)) is True:
            logger.debug(f'亀裂のAPI ID: {fissure.api_id} この亀裂は終了してる')
            embed = warframe_fissures_embed(fissure.node, fissure.type, fissure.enemy, fissure_tier_conversion(fissure.tier), '終了済み')
        else:
            logger.debug(f'亀裂のAPI ID: {fissure.api_id} この亀裂は終了していない')
            embed = warframe_fissures_embed(fissure.node, fissure.type, fissure.enemy, fissure_tier_conversion(fissure.tier), mission_eta_conversion(fissure.eta))
        await get_message.edit(embed=embed)
    # データに登録されている亀裂が期限切れになっていないかを確認
    for test in session.query(WarframeFissuresDetail).all():
        if bool(strtobool(test.status)) is True:
            await db_manager.commit(session.delete(session.query(WarframeFissuresId).filter(WarframeFissuresId.api_id == f'{test.api_id}').first()), commit_type='delete', show_commit_log=False)


class Ssm(commands.Bot):

    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, help_command=None, description=None, intents=intents)
        slash = SlashCommand(self, sync_commands=True)

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        spinner.stop()
        loop_bot_task.start()
        if bool(strtobool(use_api)) is True:
            api_request.start()
        if bool(strtobool(use_eew)) is True:
            await bot_eew_loop.start()
        print('--------------------------------')
        print(self.user.name)
        print(self.user.id)
        print('--------------------------------')

    async def on_message(self, ctx):
        if bool(strtobool(show_bot_chat_log)) is False and ctx.author.bot is True:
            return
        logger.info(f'{ctx.guild.name}=> {ctx.channel.name}=> {ctx.author.name}: {ctx.content}')
        if ctx.embeds:
            for embed in ctx.embeds:
                logger.info(embed.to_dict())
        check_voice_channel = discord.utils.get(self.voice_clients, guild=ctx.guild)  # This allows for more functionality with voice channels

        if bool(strtobool(read_aloud)) is True and check_voice_channel is not None:
            create_wave(f'{ctx.content}')
            source = discord.FFmpegPCMAudio(f"{Output_wav_name}")
            try:
                ctx.guild.voice_client.play(source)
            except AttributeError:
                pass
        await bot.process_commands(ctx)  # コマンド動作用


async def bot_run(bot_loop):
    asyncio.set_event_loop(bot_loop)
    await bot.start(f'{bot_token}')


async def api_run(loop1):
    asyncio.set_event_loop(loop1)
    config = Config(app=app, host="0.0.0.0", loop=loop1, port=5000, reload=True)
    server = Server(config)
    await server.serve()


def run(loop_bot, loop_api):
    global bot
    global slash_client
    AutoMigrate().generate()
    asyncio.set_event_loop(loop_bot)
    intents = discord.Intents.all()
    bot = Ssm(command_prefix=f'{bot_prefix}', intents=intents)
    if bool(strtobool(use_api)) is True:
        future = asyncio.gather(bot_run(loop_bot), api_run(loop_api))
    else:
        future = asyncio.gather(bot_run(loop_bot))
    loop_bot.run_until_complete(future)

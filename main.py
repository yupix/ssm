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
from modules.create_logger import easy_logger

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

while True:
	try:
		cnx = mysql.connector.connect(
			host=f'{db_host}',
			port=f'{db_port}',
			user=f'{db_user}',
			password=f'{db_password}',
			database=f'{db_default_database}'
		)
		logger.info(f'データベースへの接続に成功しました')
		break
	except mysql.connector.Error as err:
		if err.errno == 2003:
			logger.error(f'{db_host}に接続できませんでした。3秒後に自動でリトライします')
		elif err.errno == 1698:
			logger.error(f'{db_user}@{db_host}で認証に失敗しました。3秒後に自動でリトライします')
		time.sleep(3)
cnx.ping(reconnect=True)
db_cursor = cnx.cursor()

INITIAL_EXTENSIONS = [
	'cogs.testcog',
	'cogs.blogcog',
	'cogs.basiccog',
	'cogs.blocklistcog',
	'cogs.modpackcog',
	'cogs.hostlabcog',
	'cogs.read',
	'cogs.note',
	'cogs.emoji',
	'cogs.pso2',
	'cogs.rss',
	'cogs.level'
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
			#await ctx.send(f'{error_message}')
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


async def embed_send(ctx, bot, embed_type, title, subtitle, color = None):
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


async def db_update(table_name, table_column, val):
	sql = f'UPDATE {table_name} SET {table_column}'
	db_cursor.execute(sql, val)
	cnx.commit()


async def db_insert(sql, val):
	db_cursor.execute(sql, val)
	cnx.commit()
	return db_cursor.lastrowid

async def db_get_auto_increment():  # TODO: 2020/12/06/ この関数の削除
	db_cursor.execute(
		f'SELECT last_insert_id();')
	myresult = db_cursor.fetchall()
	result = await db_reformat(myresult, 2)
	return result


async def db_search(table_name=None, table_column=None, where_condition=None, custom=None):
	if table_name and table_column and where_condition:
		db_cursor.execute(
			f'SELECT {table_name} FROM {table_column} WHERE {where_condition}')
		myresult = db_cursor.fetchall()
		return myresult
	else:
		logger.debug(custom)
		db_cursor.execute(
			f'SELECT {custom}')
		myresult = db_cursor.fetchall()
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
	db_cursor.execute(sql, adr)

	cnx.commit()


def json_load(path):
	json_open = open(f'{path}', 'r')
	json_load = json.load(json_open)
	return json_load

def create_default_table():
	db_cursor.execute('USE default_discord')

	# discord_reaction_data を作る
	database_table_list_load = json_load("./template/database_table.json")

	for x in database_table_list_load.keys():
		if f'{x}' == 'delete':
			for n in database_table_list_load[x]['table']:
				get_table_name = database_table_list_load[f'{x}']['table'][f'{n}']
				sql = (f'DROP TABLE IF EXISTS {get_table_name}')
				db_cursor.execute(sql)
		elif f'{x}' == 'create':
			for n in database_table_list_load[f'{x}']['table']:
				set_column = ""
				for i in database_table_list_load[f'{x}']['table'][f'{n}']['column']:
					get_column = database_table_list_load[f'{x}']['table'][f'{n}']['column'][f'{i}']
					set_column += get_column + ', '
				db_cursor.execute(
					f'CREATE TABLE IF NOT EXISTS {n} ({set_column[:-2]})')


def check_database():
	print(reset_status)
	if f'{reset_status}' == '1':
		logger.info('データベースの初期化確認に成功')
	else:
		logger.info('データベースを初期化中です...')
		db_cursor.execute('DROP DATABASE IF EXISTS default_discord')
		db_cursor.execute('CREATE DATABASE default_discord')

		config.set('RESET', 'Status', '1')
		with open('config.ini', 'w') as configfile:
			config.write(configfile)

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
		logger.info(f'{ctx.guild.name}=> {ctx.channel.name}=> {ctx.author.name}: {ctx.content}')
		#print(f'[[ 発言 ]] {ctx.guild.name}=> {ctx.channel.name}=> {ctx.author.name}: {ctx.content}')
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

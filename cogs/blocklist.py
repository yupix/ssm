import datetime
from logging import getLogger

import discord
import typing
from discord import NotFound, HTTPException
from discord.ext import commands
from sqlalchemy import and_

from base import db_manager, use_language
from main import embed_send, bot_prefix
from modules.language_manager import LanguageManager
from settings import session
from sql.models.basic import Reactions
from sql.models.blocklist import BlocklistServer, BlocklistSettings, BlocklistUser

logger = getLogger('main').getChild('blocklist')

language = LanguageManager(base_path='./language/', lang=f'{use_language}', module_name='blocklist').get()


# noinspection StrFormat
class BlockList:
	def __init__(self, reactions=None, bot=None):
		self.reactions = reactions
		self.bot = bot

	async def reaction(self):
		target_user_id = int(self.reactions.content['target_user_id'])
		target_user_mode = str(self.reactions.content['mode'])

		user = self.bot.get_user(target_user_id)
		embed_title = str(language['reactions'][f'{self.reactions.type}']['title']).format(user.name)
		embed_subtitle = language['reactions'][f'{self.reactions.type}']['subtitle']
		msg_channel = self.bot.get_channel(self.reactions.channel_id)
		msg = await msg_channel.fetch_message(self.reactions.message_id)
		embed = discord.Embed(title=embed_title,
		                      description=embed_subtitle, color=0x8bc34a)
		if self.reactions.type == 'register':
			await db_manager.commit(BlocklistUser(server_id=self.reactions.guild_id, user_id=target_user_id, mode=target_user_mode))
		await msg.edit(embed=embed)

async def blog_reaction(reaction, reformat_mode, user, msg, reformat_check_reaction):
	if reformat_mode == '0':
		embed_title = f'{user.name} さんをブロックリストに登録しました'
		embed_sub_title = 'サーバーに平和が訪れることを祈ります'

		cancel_embed_title = f'{user.name} さんのブロックリスト登録をキャンセルしました'
		cancel_embed_sub_title = '平和が一番ですよね♪'

	elif reformat_mode == '1':
		embed_title = f'{user.name} さんのブロックリストを解除しました'
		embed_sub_title = '問題が発生しないことを祈ります'

		cancel_embed_title = f'{user.name} さんのブロックリスト解除をキャンセルしました'
		cancel_embed_sub_title = '無理に解除する必要性はありません！'

	embed_color = 0x8bc34a
	if reaction.emoji == '✅':

		embed = discord.Embed(title=f'{embed_title}',
		                      description=f'{embed_sub_title}', color=embed_color)
		await msg.edit(embed=embed)
		print(reformat_mode)
		if reformat_mode == '0':
			date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			db_cursor.execute(f'INSERT INTO blocklists (created_at) VALUES (\'{date}\')')
			cnx.commit()

			reaction_id = await db_get_auto_increment()  # auto_incrementのidを取得
			search_reaction_id = await db_reformat(await db_search('id', 'reactions', f'message_id = {msg.id}'), 2)  # reaction_idを取得
			search_mode = await db_reformat(await db_search('block_mode', 'blocklist_reaction', f'server_id = {msg.guild.id} AND reaction_id = {search_reaction_id}'), 1)  # modeを取得
			print(f'mode: {search_mode}')
			print(f'ユーザー{user.id}')
			sql = "INSERT INTO blocklist_user (block_id, server_id, user_id, mode) VALUES (%s, %s, %s, %s)"
			val = (reaction_id, msg.guild.id, user.id, search_mode)
			await db_insert(sql, val)

		elif reformat_mode == '1':
			search_blocklist_id = await db_reformat(await db_search('block_id', 'blocklist_user', f'server_id = {msg.guild.id} AND user_id = {user.id}'), 2)  # blocklist_idを取得
			sql = f'DELETE FROM blocklists WHERE id = %s'
			adr = (search_blocklist_id,)
			db_cursor.execute(sql, adr)

			cnx.commit()

		await db_delete('reactions', 'message_id = %s', f'{msg.guild.id}')  # embedのデータを削除
	elif reaction.emoji == '✖':
		embed = discord.Embed(title=cancel_embed_title,
		                      description=cancel_embed_sub_title, color=embed_color)
		await msg.edit(embed=embed)
		await db_delete('reactions', 'message_id = %s', f'{reformat_check_reaction}')


class BlocklistCog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.group()
	async def blocklist(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('this command is sub option required')

	@blocklist.command()
	async def register(self, ctx, mode='autokick', role: discord.Role=None):
		if ctx.author.guild_permissions.administrator:
			search_blocklist_server = session.query(BlocklistServer).filter(BlocklistServer.server_id == f'{ctx.guild.id}').first()
			if not search_blocklist_server:  # サーバーIDが既に登録されてるか確認
				await db_manager.commit(BlocklistServer(server_id=f'{ctx.guild.id}'))

			search_blocklist_server_settings = session.query(BlocklistSettings).filter(BlocklistSettings.server_id == f'{ctx.guild.id}').first()

			if not search_blocklist_server_settings:  # 既に設定が存在するか確認
				processing_mode_list = ['autokick', 'autoban', 'addrole', 'removerole']
				for check_mode in processing_mode_list:
					if f'{mode}' == f'{check_mode}':  # 存在するmodeか確認
						logger.debug('モードの確認に成功しました')
						if f'{mode}' == 'nonerole' or f'{mode}' == 'addrole':
							role_id = role.id
						else:
							role_id = None
						await db_manager.commit(BlocklistSettings(server_id=ctx.guild.id, mode=mode, role=role_id))
						await embed_send(ctx, self.bot, 0, '成功', '設定を保存しました!')
						break
				else:
					await embed_send(ctx, self.bot, 1, 'エラー', '存在しないモードです')
			else:
				await embed_send(ctx, self.bot, 1, 'エラー', '既に設定が存在します')

	@blocklist.command()
	async def add(self, ctx, user: discord.User = None, mode: typing.Optional[str] = None):
		if ctx.author.guild_permissions.administrator:
			search_blocklist_server_settings = session.query(BlocklistSettings).filter(BlocklistSettings.server_id == f'{ctx.guild.id}').first()
			if mode is not None:
				processing_mode_list = ['autokick', 'autoban', 'addrole', 'removerole']
				for check_mode in processing_mode_list:
					if f'{mode}' == f'{check_mode}':  # 存在するmodeか確認
						if search_blocklist_server_settings:  # サーバーIDが既に登録されてるか確認
							search_blocklist_user = session.query(BlocklistUser).filter(and_(BlocklistUser.server_id == f'{ctx.guild.id}', BlocklistUser.user_id == f'{user.id}')).first()

							if search_blocklist_user is None:
								embed = discord.Embed(title=f"{user.name} をブロックリストに登録しますか？",
								                      description="怒りに我を忘れていないかもう一度冷静になって確認してみましょう\n問題が無いようなら✅を押してください。",
								                      color=0xffc629)
								msg = await ctx.send(embed=embed)
								await msg.add_reaction('✅')
								await msg.add_reaction('✖')
								await db_manager.commit(Reactions(guild_id=msg.guild.id, channel_id=msg.channel.id, message_id=msg.id, type='register', action='BlockList', content={"target_user_id": f"{user.id}", "mode": f"{mode}"}, module_path='cogs.blocklist',class_name='BlockList'))
							else:
								await embed_send(ctx, self.bot, 1, 'エラー', '既に登録されているユーザーです')

						else:
							await embed_send(ctx, self.bot, 1, 'エラー', f'サーバーが登録されていません。\n`{bot_prefix}blocklist register mode role`\nを実行した後に再度実行してください。')
						break
				else:
					await embed_send(ctx, self.bot, 1, 'エラー', '存在しないモードです')

	@blocklist.command()
	async def remove(self, ctx, user_id):
		if ctx.author.guild_permissions.administrator:
			try:
				user = await self.bot.fetch_user(user_id)
				search_blocklist_id, search_blocklist_server_id, search_blocklist_user_id = await blocklist_information(ctx, user)

				if search_blocklist_user_id:
					embed = discord.Embed(title=f"{user.name} をブロックリストから解除しますか？",
					                      description="最後にもう一度、本当に解除しても問題ないですか？\n問題が無いようなら✅を押してください。", color=0xffc629)
					msg = await ctx.send(embed=embed)
					await msg.add_reaction('✅')
					await msg.add_reaction('✖')

					sql = "INSERT INTO reactions (message_id) VALUES (%s)"
					val = (msg.id,)
					await db_insert(sql, val)

					search_reaction_id = await db_reformat(await db_search('id', 'reactions', f'message_id = {msg.id}'), 2)

					sql = "INSERT INTO blocklist_reaction (reaction_id, server_id, channel_id, user_id, command, mode, block_mode) VALUES (%s, %s, %s, %s, %s, %s, %s)"
					val = (search_reaction_id, msg.guild.id, msg.channel.id, user.id, 'blocklist', 1, f'None')
					await db_insert(sql, val)
				else:
					await embed_send(ctx, self.bot, 1, 'エラー', '登録されていないユーザーです')
			except NotFound:
				await embed_send(ctx, self.bot, 1, 'エラー', '存在しないユーザーです')
			except HTTPException:
				await embed_send(ctx, self.bot, 1, 'エラー', '取得時にエラーが発生しました')

	@blocklist.command()
	async def list(self, ctx):
		if ctx.author.guild_permissions.administrator:
			search_block_id = await db_search('block_id', 'blocklist_user', f'server_id = {ctx.guild.id}')
			search_user_id = await db_search('user_id', 'blocklist_user', f'server_id = {ctx.guild.id}')

			for i in range(len(search_block_id)):
				print(search_block_id)
				block_id = await db_reformat(f'{search_block_id[-i]}', 1)
				user_id = await db_reformat(f'{search_user_id[-i]}', 1)
				print(f'{block_id}', f'{user_id}')
		else:
			await ctx.send('このコマンドには管理者必須やで')


def setup(bot):
	bot.add_cog(BlocklistCog(bot))

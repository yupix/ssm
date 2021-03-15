import datetime
from logging import getLogger

import discord
import typing
from discord import NotFound, HTTPException
from discord.ext import commands
from discord.ext.commands import has_permissions
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
	def __init__(self, reactions=None, bot=None, emoji=None):
		self.reactions = reactions
		self.bot = bot
		self.emoji = emoji

	async def reaction(self):
		target_user_id = int(self.reactions.content['target_user_id'])
		user = self.bot.get_user(int(target_user_id))
		if self.emoji == '✅':
			action = 'continue'
		elif self.emoji == '✖':
			action = 'cancel'
		# TODO: 2021/3/15 elseで他のリアクションだったときの動作を作る

		embed_title = str(language['BlocklistReactions'][f'{self.reactions.type}'][f'{action}']['title']).format(user.name)
		embed_subtitle = language['BlocklistReactions'][f'{self.reactions.type}'][f'{action}']['subtitle']
		embed_color = language['BlocklistReactions'][f'{self.reactions.type}'][f'{action}']['embed_color']
		msg_channel = self.bot.get_channel(self.reactions.channel_id)
		msg = await msg_channel.fetch_message(self.reactions.message_id)
		embed = discord.Embed(title=embed_title,
		                      description=embed_subtitle, color=int(embed_color))
		if self.reactions.type == 'register' and action != 'cancel':
			target_user_mode = str(self.reactions.content['mode'])
			await db_manager.commit(BlocklistUser(server_id=self.reactions.guild_id, user_id=target_user_id, mode=target_user_mode))
		elif self.reactions.type == 'unregister' and action != 'cancel':
			await db_manager.commit(session.query(BlocklistUser).filter(and_(BlocklistUser.server_id == self.reactions.guild_id, BlocklistUser.user_id == target_user_id)).delete(),
			                        commit_type='delete')
		await msg.edit(embed=embed)


def check_mode(use_mode: str) -> typing.Union[str, None]:
	mode_list = ['AutoKick', 'AutoBan', 'AddRole', 'RemoveRole']
	for _mode in mode_list:
		if f'{use_mode}'.upper() == f'{_mode}'.upper():  # 存在するmodeか確認
			mode = _mode
			logger.debug('test')
			break
		else:
			mode = None
	return mode


class BlocklistCog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.group()
	async def blocklist(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('this command is sub option required')

	@blocklist.command()
	async def register(self, ctx, mode='AutoKick', add_role: discord.Role = None, remove_role: discord.Role = None):
		if ctx.author.guild_permissions.administrator:
			search_blocklist_server = session.query(BlocklistServer).filter(BlocklistServer.server_id == f'{ctx.guild.id}').first()
			if not search_blocklist_server:  # サーバーIDが既に登録されてるか確認
				await db_manager.commit(BlocklistServer(server_id=f'{ctx.guild.id}'))

			search_blocklist_server_settings = session.query(BlocklistSettings).filter(BlocklistSettings.server_id == f'{ctx.guild.id}').first()

			if not search_blocklist_server_settings:  # 既に設定が存在するか確認
				processing_mode_list = ['AutoKick', 'AutoBan', 'AddRole', 'RemoveRole']
				for check_mode in processing_mode_list:
					if f'{mode}' == f'{check_mode}':  # 存在するmodeか確認
						logger.debug('モードの確認に成功しました')
						if f'{mode}' == 'NoneRole' or f'{mode}' == 'AddRole' or f'{mode}' == 'RemoveRole':
							add_role = add_role.id
							remove_role = remove_role.id
						else:
							add_role = None
							remove_role = None
						await db_manager.commit(BlocklistSettings(server_id=ctx.guild.id, mode=mode, add_role=add_role, remove_role=remove_role))
						await embed_send(ctx, self.bot, 0, '成功', '設定を保存しました!')
						break
				else:
					await embed_send(ctx, self.bot, 1, 'エラー', '存在しないモードです')
			else:
				await embed_send(ctx, self.bot, 1, 'エラー', '既に設定が存在します')

	@blocklist.command()
	@has_permissions(manage_guild=True)
	async def add(self, ctx, user: discord.User=None, mode: check_mode=None):
		search_blocklist_server_settings = session.query(BlocklistSettings).filter(BlocklistSettings.server_id == f'{ctx.guild.id}').first()
		if mode is not None:
			if search_blocklist_server_settings:  # サーバーIDが既に登録されてるか確認
				search_blocklist_user = session.query(BlocklistUser).filter(and_(BlocklistUser.server_id == f'{ctx.guild.id}', BlocklistUser.user_id == f'{user.id}')).first()

				if search_blocklist_user is None:
					embed = discord.Embed(title=f"{user.name} をブロックリストに登録しますか？",
					                      description="怒りに我を忘れていないかもう一度冷静になって確認してみましょう\n問題が無いようなら✅を押してください。",
					                      color=0xffc629)
					msg = await ctx.send(embed=embed)
					await msg.add_reaction('✅')
					await msg.add_reaction('✖')
					await db_manager.commit(Reactions(guild_id=msg.guild.id, channel_id=msg.channel.id, message_id=msg.id, type='register', action='BlockList',
					                                  content={"target_user_id": f"{user.id}", "mode": f"{mode}"}, module_path='cogs.blocklist', class_name='BlockList'))
				else:
					await embed_send(ctx, self.bot, 1, 'エラー', '既に登録されているユーザーです')

			else:
				await embed_send(ctx, self.bot, 1, 'エラー', f'サーバーが登録されていません。\n`{bot_prefix}blocklist register mode role`\nを実行した後に再度実行してください。')
		else:
			await embed_send(ctx, self.bot, 1, 'エラー', f'{mode}は存在しないモードです')

	@add.error
	async def add_error(self, ctx, error):
		if isinstance(error, commands.UserNotFound):
			await embed_send(ctx, self.bot, 1, '失敗', '存在しないユーザーです')

	@blocklist.command()
	@has_permissions(manage_guild=True)
	async def remove(self, ctx, user: discord.User):
		search_blocklist_user = session.query(BlocklistUser).filter(and_(BlocklistUser.server_id == f'{ctx.guild.id}', BlocklistUser.user_id == f'{user.id}')).first()

		if search_blocklist_user:
			embed = discord.Embed(title=f"{user.name} をブロックリストから解除しますか？",
			                      description="最後にもう一度、本当に解除しても問題ないですか？\n問題が無いようなら✅を押してください。", color=0xffc629)
			msg = await ctx.send(embed=embed)
			await msg.add_reaction('✅')
			await msg.add_reaction('✖')

			await db_manager.commit(Reactions(guild_id=msg.guild.id, channel_id=msg.channel.id, message_id=msg.id, type='unregister', action='BlockList',
			                                  content={"target_user_id": f"{user.id}"}, module_path='cogs.blocklist', class_name='BlockList'))
		else:
			await embed_send(ctx, self.bot, 1, 'エラー', '登録されていないユーザーです')

	@remove.error
	async def reload_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			await embed_send(ctx, self.bot, 1, '失敗', 'このコマンドはBotの所有者のみが実行できます')

	@blocklist.command()
	@has_permissions(manage_guild=True)
	async def list(self, ctx):
		search_blocklist_users = session.query(BlocklistUser).filter(BlocklistUser.server_id == f'{ctx.guild.id}').all()
		guild = self.bot.get_guild(ctx.guild.id)
		embed = discord.Embed(title=f'{guild.name}のブロックリスト',color=0x859fff)
		for _user in search_blocklist_users:
			if len(embed) < 1800:
				user = self.bot.get_user(_user.user_id)
				embed.add_field(name=f"ユーザー名: {user.name}", value=f"理由: 無し", inline=True)
		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(BlocklistCog(bot))

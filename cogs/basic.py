import asyncio
import traceback
from logging import getLogger

import discord
from discord.ext import commands
from discord.utils import get
from sqlalchemy import and_

from main import Output_wav_name, INITIAL_EXTENSIONS, embed_send
from modules.voice_generator import create_wave
from settings import session
from sql.models.basic import Reactions
from sql.models.blocklist import BlocklistUser, BlocklistSettings

logger = getLogger('main').getChild('basic')


class BlocklistAction:
	def __init__(self, search_guild=None, search_user=None, member: discord.Member = None):
		self.search_guild = search_guild
		self.search_user = search_user
		self.member = member

	async def check_blocklist(self):
		if self.search_user is not None:
			logger.debug(f'{self.member.name}はギルド{self.member.guild.name}のブロックリストに登録されています')
		else:
			logger.debug(f'{self.member.name}はギルド{self.member.guild.name}のブロックリストに登録されていません')
		registered = self.search_user
		await self.check_mode(registered)

	async def check_role(self, mode):
		mode_list = ['AutoKick', 'AutoBan', 'AddRole', 'RemoveRole']
		if mode in mode_list:
			if self.search_guild is not None:
				try:
					role = self.search_guild.role
				except AttributeError:
					role = None
			else:
				role = None
			return role
		else:
			return None

	async def check_mode(self, registered):
		if self.search_user is None:  # ユーザーのモードを優先
			mode = self.search_guild.mode
		else:
			mode = self.search_user.mode
		role = await self.check_role(mode)
		if mode == 'AutoKick':
			await self.auto_kick(registered)
		elif mode == 'AutoBan':
			await self.auto_ban(registered)
		elif mode == 'AddRole':
			await self.add_role(registered, role)
		elif mode == 'RemoveRole':
			pass

	async def auto_kick(self, registered):
		"""ユーザーがブロックリストに存在する場合ユーザーをKickします"""
		if registered is not None:
			await self.member.kick()
		return 'success'

	async def auto_ban(self, registered):
		"""ユーザーがブロックリストに存在する場合ユーザーをBANします"""
		if registered is not None:
			await self.member.ban()
		return 'success'

	async def add_role(self, registered, role):
		"""ユーザーがブロックリストに存在する場合ロールを付与します"""
		if registered is not None:  # ユーザーが登録されている場合
			await self.member.add_role(role)
		return 'success'

	async def remove_role(self, registered, role):
		"""ユーザーがブロックリストに存在する場合は権限を付与しません"""
		if registered is None:
			await self.member.add_role(role)
		return 'success'

class BasicCog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def ping(self, ctx):
		await ctx.channel.send(f'ping: {round(self.bot.latency * 1000)}ms')

	@commands.command(name='reload')
	@commands.is_owner()
	async def reload(self, ctx):
		for cog in INITIAL_EXTENSIONS:
			try:
				self.bot.reload_extension(cog)
			except Exception:
				traceback.print_exc()
		logger.info('リロードに成功しました')
		await embed_send(ctx, self.bot, 0, '成功', 'リロードに成功しました！')
		return ctx

	@reload.error
	async def reload_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			await embed_send(ctx, self.bot, 1, '失敗', 'このコマンドはBotの所有者のみが実行できます')

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		search_user = session.query(BlocklistUser).filter(and_(BlocklistUser.server_id == f'{member.guild.id}', BlocklistUser.user_id == f'{member.id}')).first()
		search_guild = session.query(BlocklistSettings).filter(BlocklistSettings.server_id == member.guild.id).first()
		blocklist_action = BlocklistAction(search_guild=search_guild, search_user=search_user, member=member)
		await blocklist_action.check_blocklist()

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		logger.debug(f'{member.id}, {self.bot.user.id}')
		if member.id == self.bot.user.id:
			return
		elif member.bot:
			input_text = 'ボット: '
		else:
			input_text = 'ユーザー: '

		if before.channel is None:
			logger.debug(f'{member.name} さんがボイスチャンネル {after.channel.name} に参加しました')
			create_wave(input_text + f'{member.name} さんがボイスチャンネルに参加しました')
		elif after.channel is None:
			logger.debug(f'{member.name} さんがボイスチャンネル {before.channel.name} から退出しました')
			create_wave(input_text + f'{member.name} さんがボイスチャンネルから退出しました')

		if before.channel is None or after.channel is None:
			source = discord.FFmpegPCMAudio(f"{Output_wav_name}")
			while True:
				if member.guild.voice_client:
					if member.guild.voice_client.is_playing() is False:
						member.guild.voice_client.play(source)
						break
					await asyncio.sleep(3)
				else:
					break

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):

		if user == self.bot.user:
			return
		emoji = reaction.emoji
		reaction_message_id = reaction.message.id  # リアクションが付いたメッセージID
		reaction_channel_id = reaction.message.channel.id  # リアクションが付いたメッセージのあるチャンネルID
		reaction_guild_id = reaction.message.guild.id  # リアクションが付いたメッセージのあるギルド
		logger.debug(f'リアクションがついたメッセージID: {reaction_message_id}')
		logger.debug(f'リアクションがついたメッセージのあるチャンネル: {reaction_channel_id}')
		logger.debug(f'リアクションが付いたメッセージのあるギルド: {reaction_guild_id}')

		reactions = session.query(Reactions).filter(Reactions.message_id == reaction_message_id).first()
		print(reactions)
		if reactions:
			exec(f'from {reactions.module_path} import {reactions.class_name}')
			cls = eval(reactions.action)(reactions, self.bot, emoji)
			await getattr(cls, 'reaction')()


def setup(bot):
	bot.add_cog(BasicCog(bot))

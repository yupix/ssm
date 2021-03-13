import asyncio
import traceback
from logging import getLogger

import discord
from discord.ext import commands
from discord.utils import get

from main import Output_wav_name, INITIAL_EXTENSIONS, embed_send
from modules.voice_generator import create_wave
from settings import session
from sql.models.basic import Reactions

logger = getLogger('main').getChild('basic')

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
		async def blockuser_treatment(search_blocklist_mode, member):
			print(search_blocklist_mode)
			print(member)
			if f'{search_blocklist_mode}' == 'autokick':  # ブロックユーザーには権限を付与しないモード
				await member.kick()
			elif f'{search_blocklist_mode}' == 'autoban':  # ブロックユーザーには権限を付与しないモード
				await member.ban()

		search_server_id = await db_reformat(
			await db_search('server_id', 'blocklist_server', f'server_id = {member.guild.id}'), 2)
		if search_server_id:
			search_blocklist_mode = await db_reformat(
				await db_search('mode', 'blocklist_settings', f'server_id = {member.guild.id}'), 1)
			check_block_list = await db_search('user_id', 'blocklist_user', f'server_id = {member.guild.id} AND user_id = {member.id}')
			if check_block_list:
				print('ブロックユーザーです')
				search_blocklist_user_mode = await db_reformat(await db_search('mode', 'blocklist_user',
				                                                               f'server_id = {member.guild.id} AND user_id = {member.id}'), 1)

				if f'{search_blocklist_user_mode}' != 'None':
					await blockuser_treatment(search_blocklist_user_mode, member)
					print('ユーザー処理されました')
				else:
					await blockuser_treatment(search_blocklist_mode, member)
					print('デフォルト処理されました')

			else:
				print('ブロックリストじゃないよ')
				if f'{search_blocklist_mode}' == 'nonerole':  # ブロックユーザーには権限を付与しないモード
					role_id = await db_search('role_id', 'blocklist_role',
					                          f'server_id = {member.guild.id}')
					reformat_role_id = await db_reformat(role_id, 2)
					role = get(member.guild.roles, id=reformat_role_id)
					print(f'{role.name}')
					await member.add_roles(role)

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
			cls = eval(reactions.action)(reactions, self.bot)
			await getattr(cls, 'reaction')()

def setup(bot):
	bot.add_cog(BasicCog(bot))

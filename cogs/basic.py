import asyncio
import traceback

import discord
from discord.ext import commands
from discord.utils import get

from cogs.blocklist import blog_reaction
from main import logger, Output_wav_name, INITIAL_EXTENSIONS, embed_send
from modules.voice_generator import create_wave


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

		search_reaction = await db_reformat(await db_search('message_id', 'reactions', f'message_id = {reaction_message_id}'), 2)
		search_reaction_id = await db_reformat(await db_search('id', 'reactions', f'message_id = {reaction_message_id}'), 2)

		if search_reaction:
			check_channel = await db_reformat(
				await db_search('channel_id', 'blocklist_reaction', f'channel_id = {reaction_channel_id}'), 2)

			check_user = await db_reformat(
				await db_search('user_id', 'blocklist_reaction', f'channel_id = {reaction_channel_id} AND reaction_id ={search_reaction_id} AND user_id IS NOT NULL'), 2)

			user = await self.bot.fetch_user(check_user)

			check_command = await db_reformat(
				await db_search('command', 'blocklist_reaction', f'channel_id = {reaction_channel_id} AND reaction_id ={search_reaction_id} AND command IS NOT NULL'), 1)

			"""現状使わないのでコメントアウト
			check_original_message_id = await db_search('original_message_id', 'discord_reaction',
											f'channel_id = {reaction_channel_id} AND message_id = {reaction_message_id} AND original_message_id IS NOT NULL')
			reformat_original_message_id = await db_reformat(check_original_message_id, 1)
			"""

			channel = reaction.message.guild.get_channel(check_channel)

			# ogl_msg = await channel.fetch_message(reformat_original_message_id)
			msg = await channel.fetch_message(reaction_message_id)

			check_mode = await db_reformat(
				await db_search('mode', 'blocklist_reaction', f'channel_id = {reaction_channel_id} AND reaction_id ={search_reaction_id} AND mode IS NOT NULL'), 1)

			print(f'見つかったチャンネルID: {check_channel}\n'
			      f'見つかったユーザーID: {check_user}\n'
			      f'見つかったコマンド: {check_command}\n'
			      f'モード: {check_mode}\n'
			      f'付けられた絵文字: {emoji}')

			if check_command == 'blocklist':
				await blog_reaction(reaction, check_mode, user, msg, search_reaction)

			"""未修正のためコメントアウト
			elif check_command == 'modpack':
				await modpack_reaction(reaction, check_mode, user, msg, search_reaction, ogl_msg)
			"""


# elif reformat_command == 'basic':
# await basic_reaction(reaction, check_mode, user, msg, search_reaction, ogl_msg)


def setup(bot):
	bot.add_cog(BasicCog(bot))

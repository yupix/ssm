import asyncio

import discord
from discord.ext import commands
from discord.utils import get

from cogs.blocklist import blog_reaction
from main import logger, Output_wav_name
from modules.voice_generator import create_wave

"""利用規約同意のデータが追加されたあとも認識しないため一時的にコメントアウト
async def basic_reaction(reaction, reformat_mode, user, msg, reformat_check_reaction, ogl_msg):

	if reformat_mode == '0':
		embed_title = f'利用規約に同意しました'
		embed_sub_title = 'ご利用ありがとうございます'

		cancele_embed_title = f'利用規約の同意をキャンセルしました'
		cancele_embed_title = 'またの機会をお待ちしています'

	elif reformat_mode == '1':
		embed_title = f'利用規約を解約しました'
		embed_sub_title = '今までのご利用ありがとうございました'
		cancele_embed_title = f'利用規約の解約をキャンセルしました'
		cancele_embed_title = '今後もよろしくおねがいします'

	embed_color = 0x8bc34a
	if reaction.emoji == '✅':

		embed = discord.Embed(title=f'{embed_title}',
							  description=f'{embed_sub_title}', color=embed_color)
		await msg.edit(embed=embed)
		print(reformat_mode)
		if reformat_mode == '0':
			check_alredy_server_register = await db_search('id', 'server_main_info',
											 f'server_id = {msg.guild.id} AND id IS NOT NULL')

			if not check_alredy_server_register:
				sql = "INSERT INTO server_main_info (server_id, consent_status) VALUES (%s, %s)"
				val = (f'{msg.guild.id}', f'Agree')

				db_cursor.execute(sql, val)
				cnx.commit()
			else:
				msg.channel.send('既に登録されています')



			cnx.commit()
"""


class BasicCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.channel.send(f'ping: {round(self.bot.latency * 1000)}ms ')

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

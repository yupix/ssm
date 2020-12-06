import discord
from discord.ext import commands
from discord.utils import get

from main import db_search, db_reformat, mycursor, mydb, db_delete, embed_send, check_url


async def modpack_reaction(reaction, reformat_mode, user, msg, reformat_check_reaction, ogl_msg):
	ogl_msg_list = str(ogl_msg.content).split()
	# print(str(ogl_msg_list[2:]))
	modpack_name = f'{ogl_msg_list[2]}'
	modpack_mc_version = f'{ogl_msg_list[3]}'
	modpack_description = f'{ogl_msg_list[4]}'
	modpack_tags = ','.join(ogl_msg_list[5:])

	print(f'ModPack名: {modpack_name}\n'
		  f'ModPackのMCバージョン: {modpack_mc_version}\n'
		  f'ModPackの説明: {modpack_description}\n'
		  f'ModPackのタグ一覧: {modpack_tags}')

	if reformat_mode == '0':
		embed_title = f'{modpack_name}を登録しました!'
		embed_sub_title = 'ModPackIDは'

		cancele_embed_title = f'ModPackの登録をキャンセルしました'
		cancele_embed_title = 'またの機会をお待ちしています'

	elif reformat_mode == '1':
		embed_title = f'{user.name} さんのブロックリストを解除しました'
		embed_sub_title = '問題が発生しないことを祈ります'
		cancele_embed_title = f'{user.name} さんのブロックリスト解除をキャンセルしました'
		cancele_embed_title = '無理に解除する必要性はありません！'

	embed_color = 0x8bc34a
	if reaction.emoji == '✅':

		embed = discord.Embed(title=f'{embed_title}',
							  description=f'{embed_sub_title}', color=embed_color)
		await msg.edit(embed=embed)
		print(reformat_mode)
		if reformat_mode == '0':
			sql = "INSERT INTO discord_modpack_main_info (author_id, pack_name, pack_mc_version) VALUES (%s, %s, %s)"
			val = (user.id, modpack_name, modpack_mc_version)
			mycursor.execute(sql, val)

			mydb.commit()

			sql = "INSERT INTO discord_modpack_sub_info (pack_description, pack_tags) VALUES (%s, %s)"
			val = (modpack_description, modpack_tags)
			mycursor.execute(sql, val)

			mydb.commit()

			get_modpack_id = await db_search('id', 'discord_modpack_main_info',
											 f'author_id = {user.id} AND pack_name = \'{modpack_name}\' AND id IS NOT NULL')

			reformat_modpack_id = await db_reformat(get_modpack_id, 2)

			print(reformat_modpack_id)

			embed = discord.Embed(title=f'{embed_title}',
								  description=f'{embed_sub_title}{reformat_modpack_id}です', color=embed_color)
			await msg.edit(embed=embed)

		# elif reformat_mode == '1':
		# sql = f'DELETE FROM discord_sub_block_list WHERE server_id = %s AND user_id = %s'
		# adr = (msg.guild.id, user.id,)
		# mycursor.execute(sql, adr)

		# mydb.commit()

		await db_delete('discord_reaction', 'message_id = %s',
						f'{reformat_check_reaction}')  # embedのデータを削除
	elif reaction.emoji == '✖':
		embed = discord.Embed(title=cancele_embed_title,
							  description=cancele_embed_title, color=embed_color)
		await msg.edit(embed=embed)
		await db_delete('discord_reaction', 'message_id = %s', f'{reformat_check_reaction}')


class ModpackCog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.group()
	async def modpack(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('this command is sub option required')

	@modpack.command()
	async def register(self, ctx, pack_name, mc_version, description, *args):
		mc_version = mc_version.replace('.', '')
		tag = ','.join(args).replace(',', ', ')
		if not tag:
			tag = '無し'
		check_alredy_register = await db_search('pack_name', 'discord_modpack_main_info',
												f'author_id = {ctx.author.id} AND pack_name = \'{pack_name}\' AND pack_name IS NOT NULL')

		if not check_alredy_register:

			embed = discord.Embed(title='登録情報の確認', description='登録したあとに内容を変更することは可能です', color=0x0f9dcc)
			embed.add_field(name='ModPack名', value=f'{pack_name}', inline=True)
			embed.add_field(name='MC VERSION', value=f'{mc_version}', inline=True)
			embed.add_field(name='タグ', value=f'{tag}', inline=True)
			embed.add_field(name='説明', value=f'{description}', inline=True)
			msg = await ctx.send(embed=embed)
			await msg.add_reaction('✅')
			await msg.add_reaction('✖')
			sql = "INSERT INTO discord_reaction (channel_id, message_id, user_id, command, mode, original_message_id) VALUES (%s, %s, %s, %s, %s, %s)"
			val = (msg.channel.id, msg.id, ctx.author.id, 'modpack', 0, ctx.message.id)

			mycursor.execute(sql, val)

			mydb.commit()

		else:
			await embed_send(ctx, self.bot, 1, 'エラー', '既に登録されているModPack名です')

	@modpack.command()
	async def add(self, ctx, pack_name, pack_url):
		print(pack_name)
		await check_url(pack_url)

	@modpack.command()
	async def check(self, ctx, pack_id):
		check_alredy_register = await db_search('id', 'discord_modpack_main_info',
												f'author_id = {ctx.author.id} AND id IS NOT NULL')
		if check_alredy_register:
			pack_name = await db_search('pack_name', 'discord_modpack_main_info',
													f'author_id = {ctx.author.id} AND id = {pack_id} AND pack_name IS NOT NULL')
			reformat_pack_name = await db_reformat(pack_name, 1)


			pack_mc_version = await db_search('pack_mc_version', 'discord_modpack_main_info',
											  f'author_id = {ctx.author.id} AND id = {pack_id} AND pack_mc_version IS NOT NULL')
			reformat_pack_mc_version = await db_reformat(pack_mc_version, 1)

			pack_description = await db_search('pack_description', 'discord_modpack_sub_info',
													f'id = {pack_id} AND pack_description IS NOT NULL')
			reformat_pack_description = await db_reformat(pack_description, 1)

			pack_tags = await db_search('pack_tags', 'discord_modpack_sub_info',
													f'id = {pack_id} AND pack_tags IS NOT NULL')

			reformat_pack_tags = await db_reformat(pack_tags, 1)
			reformat_pack_tags = reformat_pack_tags.replace(',', ', ')

			embed = discord.Embed(title='登録情報の確認', description='登録したあとに内容を変更することは可能です', color=0x0f9dcc)
			embed.add_field(name='ModPack名', value=f'{reformat_pack_name}', inline=True)
			embed.add_field(name='MC VERSION', value=f'{reformat_pack_mc_version}', inline=True)
			embed.add_field(name='タグ', value=f'{reformat_pack_tags}', inline=True)
			embed.add_field(name='説明', value=f'{reformat_pack_description}', inline=True)
			msg = await ctx.send(embed=embed)



def setup(bot):
	bot.add_cog(ModpackCog(bot))

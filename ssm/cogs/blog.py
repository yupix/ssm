import asyncio

import discord

from discord.ext import commands

from ssm import session
from ssm.base import logger, db_manager
from ssm.main import bot_prefix
from ssm.modules.embed_manager import EmbedManager
from ssm.sql.models.blog import BlogsServer, BlogsCategory, BlogsChannel


class BlogCog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	async def not_found_group(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('このコマンドには引数が必要です')

	@commands.group()
	async def blog(self, ctx):
		await self.not_found_group(ctx)

	@blog.group(name='register')
	async def _blog_register(self, ctx):
		await self.not_found_group(ctx)

	@_blog_register.command()
	async def category(self, ctx):
		await db_manager.commit(BlogsServer(server_id=ctx.guild.id))
		await db_manager.commit(BlogsCategory(server_id=ctx.guild.id, category_id=ctx.channel.category.id))
		# embed_content = [{'title': '登録に成功', 'value': f'{ctx.channel.category.name}をブログカテゴリとして登録しました', 'option': {'inline': 'True'}}]
		embed = await EmbedManager().generate(embed_title='登録に成功', embed_description=f'{ctx.channel.category.name}をブログカテゴリとして登録しました', embed_content=[])
		await ctx.send(embed=embed)

	@blog.command()
	async def setup(self, ctx):
		search_category = session.query(BlogsCategory).filter(BlogsCategory.category_id == ctx.channel.category_id).first()
		search_channel = session.query(BlogsChannel).filter(BlogsChannel.channel_id == ctx.channel.id).first()
		if search_category:
			if search_channel:
				owner = self.bot.get_user(search_channel.owner_id)
				embed = await EmbedManager().generate(embed_title='登録に失敗',
				                                       embed_description=f'`{ctx.channel.category.name}`は既に{owner.name}さんが既にブログとして登録しているチャンネルです。他のチャンネルをお使いになるか解除をお願いしてください。',
				                                       embed_content=[], mode='failed')
				await EmbedManager().send(ctx, embed, True, 5)
				return
			await db_manager.commit(BlogsChannel(category_id=ctx.channel.category.id, channel_id=ctx.channel.id, owner_id=ctx.author.id))
			embed = await EmbedManager().generate(embed_title='登録に成功',
			                                       embed_description=f'`{ctx.channel.name}`をブログとして登録しました。ようこそ{ctx.author.name}さん！',
			                                       embed_content=[], mode='succesed')

		else:
			embed = await EmbedManager().generate(embed_title='登録に失敗',
			                                       embed_description=f'`{ctx.channel.category.name}`はブログカテゴリとして登録されていません。\nブログを登録するには`{bot_prefix}blog register category`を設定したいカテゴリ内のチャンネルで実行してください。※管理者権限が必要です',
			                                       embed_content=[], mode='failed')
		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(BlogCog(bot))

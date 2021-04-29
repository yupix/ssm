import json
import math

import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from sqlalchemy import and_

from ssm import session
from ssm.base import db_manager
from ssm.main import bot_prefix
from ssm.modules.embed_manager import EmbedManager
from ssm.sql.models.blog import BlogsServer, BlogsCategory, BlogsChannel, BlogsUser

xp_increase = 12

with open(f'template/blog_achievement.json', encoding="utf-8") as f:
    get_achievement = json.load(f)


async def get_blog_info(ctx):
    search_channel = session.query(BlogsChannel).filter(BlogsChannel.channel_id == ctx.channel.id).first()
    if search_channel:
        search_user = session.query(BlogsUser).filter(and_(BlogsUser.channel_id == search_channel.channel_id, BlogsUser.user_id == ctx.author.id)).first()
    else:
        search_user = None
    return search_channel, search_user


class BlogLevelSystem:
    def __init__(self, ctx, search_channel, search_user):
        self.ctx = ctx
        self.search_channel = search_channel
        self.search_user = search_user

    async def levelup(self, next_level_up_xp, update_xp):
        current_level = self.search_user.level
        update_level = self.search_user.level + 1
        remaining_xp = int(update_xp - next_level_up_xp)
        await db_manager.commit(setattr(self.search_user, 'level', f'{update_level}'), commit_type='update', show_commit_log=False)
        await db_manager.commit(setattr(self.search_user, 'xp', f'{remaining_xp}'), commit_type='update', show_commit_log=False)
        embed = await EmbedManager().generate(embed_title='ブログユーザーレベルアップ！', embed_description=f'ブログでのユーザーレベルが{current_level} -> {update_level}に上がりました！おめでとうございます！', embed_content=[])
        await self.ctx.channel.send(embed=embed)
        if get_achievement.get('level').get(f'{update_level}'):
            achievement = get_achievement.get('level').get(f'{update_level}')
            embed = await EmbedManager().generate(embed_title=f'実績`{achievement.get("title")}`を達成', embed_description=f'{achievement.get("description")}', embed_content=[])
            await self.ctx.channel.send(embed=embed)
        return update_level

    async def xp_up(self):
        update_xp = self.search_user.xp + xp_increase
        await db_manager.commit(setattr(self.search_user, 'xp', f'{update_xp}'), commit_type='update', show_commit_log=False)
        return update_xp

    async def post_count_up(self):
        update_post_count = self.search_user.post_count + 1
        await db_manager.commit(setattr(self.search_user, 'post_count', f'{update_post_count}'), commit_type='update', show_commit_log=False)
        if get_achievement.get('post_count').get(f'{update_post_count}'):
            achievement = get_achievement.get('post_count').get(f'{update_post_count}')
            embed = await EmbedManager().generate(embed_title=f'実績`{achievement.get("title")}`を達成', embed_description=f'{achievement.get("description")}', embed_content=[])
            await self.ctx.channel.send(embed=embed)
        return update_post_count

    async def word_check(self):
        if get_achievement.get('word').get(f'{self.ctx.content}'):
            achievement = get_achievement.get('word').get(f'{self.ctx.content}')
            embed = await EmbedManager().generate(embed_title=f'実績`{achievement.get("title")}`を達成', embed_description=f'{achievement.get("description")}', embed_content=[])
            await self.ctx.channel.send(embed=embed)

    async def check(self):
        """2500 * 5^2"""
        post_count = await self.post_count_up()
        next_level_up_xp = int(1500 * (int(self.search_user.level) + 1) ^ 2)  # レベルアップに必要な経験値
        update_xp = await self.xp_up()
        if update_xp >= next_level_up_xp:
            update_level = await self.levelup(next_level_up_xp, update_xp)
        await self.word_check()


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

    @cog_ext.cog_subcommand(base="blog", name="setup", guild_ids=[530299114387406860], description='指定、実行したチャンネルをブログとして登録します')
    async def setup(self, ctx: SlashContext, channel: discord.abc.GuildChannel = None):
        if not channel:
            channel = ctx.channel

        search_category = session.query(BlogsCategory).filter(BlogsCategory.category_id == channel.category_id).first()
        search_channel = session.query(BlogsChannel).filter(BlogsChannel.channel_id == channel.id).first()
        if search_category:
            if search_channel:
                owner = self.bot.get_user(search_channel.owner_id)
                embed = await EmbedManager().generate(embed_title='登録に失敗',
                                                      embed_description=f'`{channel.category.name}`は既に{owner.name}さんが既にブログとして登録しているチャンネルです。他のチャンネルをお使いになるか解除をお願いしてください。',
                                                      embed_content=[], mode='failed')
                await EmbedManager().send(ctx, embed, True, 5)
                return
            await db_manager.commit(BlogsChannel(category_id=channel.category.id, channel_id=channel.id, owner_id=ctx.author.id))
            await db_manager.commit(BlogsUser(user_id=ctx.author.id, channel_id=channel.id))
            embed = await EmbedManager().generate(embed_title='登録に成功',
                                                  embed_description=f'`{channel.name}`をブログとして登録しました。ようこそ{ctx.author.name}さん！',
                                                  embed_content=[], mode='succesed')
        else:
            embed = await EmbedManager().generate(embed_title='登録に失敗',
                                                  embed_description=f'`{channel.category.name}`はブログカテゴリとして登録されていません。\nブログを登録するには`{bot_prefix}blog register category`を設定したいカテゴリ内のチャンネルで実行してください。※管理者権限が必要です',
                                                  embed_content=[], mode='failed')
        await ctx.send(embed=embed)

    @blog.group(name='user')
    async def user(self, ctx):
        await self.not_found_group(ctx)

    @cog_ext.cog_subcommand(base="blog", subcommand_group='user', name="profile", guild_ids=[530299114387406860], description='ブログでのプロフィールを表示します')
    async def profile(self, ctx: SlashContext):
        search_channel, search_user = await get_blog_info(ctx)
        if not search_channel:
            embed = await EmbedManager().generate(embed_title='プロフィールの表示に失敗', embed_description=f'`{ctx.channel.name}`はブログとして登録されていません。\n`{bot_prefix}blog setup`を実行したうえで再度実行してください`', embed_content=[],
                                                  mode='failed')
            await EmbedManager().send(ctx, embed, True, 3)
            return
        elif not search_user:
            return
        require_levelup_xp = int(1500 * (int(search_user.level) + 1) ^ 2)
        update_xp_parcent = math.ceil(int((search_user.xp + xp_increase) / require_levelup_xp * 100))

        embed_content = [{'title': '投稿数', 'value': f'{search_user.post_count}', 'option': {'inline': 'False'}}, {'title': '称号', 'value': f'なし', 'option': {'inline': 'False'}},
                         {'title': 'レベル', 'value': f'{search_user.level}'},
                         {'title': '経験値', 'value': f'{search_user.xp}'}, {'title': '次のレベルまで', 'value': f'{update_xp_parcent}/100%'}]
        embed = await EmbedManager().generate(embed_title=f'{ctx.author.name}のプロフィール', embed_description=f'{ctx.channel.name}での活動状況です', embed_content=embed_content,
                                              embed_thumbnail=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return
        if ctx.content != f'{bot_prefix}blog user profile':  # blog statusコマンドが投稿にカウントされないように
            search_channel = session.query(BlogsChannel).filter(BlogsChannel.channel_id == ctx.channel.id).first()
            if search_channel:
                search_user = session.query(BlogsUser).filter(and_(BlogsUser.channel_id == search_channel.channel_id, BlogsUser.user_id == ctx.author.id)).first()
                if search_user:
                    await BlogLevelSystem(ctx, search_channel, search_user).check()


def setup(bot):
    bot.add_cog(BlogCog(bot))

import datetime

import discord
from discord import NotFound, HTTPException
from discord.ext import commands
from discord.utils import get
from sqlalchemy import and_

from ssm import session
from ssm.base import db_manager
from ssm.main import embed_send, none_check_invoked_subcommand, bot_prefix
from ssm.sql.models.blog import BlogsServer, BlogsCategory


async def blog_information(ctx):
    search_blog_id = await db_reformat(await db_search('blog_id', 'blog_server', f'server_id = {ctx.guild.id}'), 2)  # blog_idを取得
    search_server_id = await db_reformat(await db_search('server_id', 'blog_server', f'server_id = {ctx.guild.id}'), 2)  # server_idを取得
    search_category_id = await db_reformat(await db_search('category_id', 'blog_category', f'category_id = {ctx.channel.category.id}'), 2)  # category_idを取得
    search_channel_id = await db_reformat(await db_search('channel_id', 'blog_channel', f'channel_id = {ctx.channel.id}'), 2)  # channel_idを取得

    return search_blog_id, search_server_id, search_category_id, search_channel_id


async def blog_level_system(ctx, execution_user_id, type):
    if type == 0:
        info_table_name = 'blog_sub_info'
        xp_info_table_name = 'blog_channel_xp'
        channel_insert_id_column = 'id'
        default_level_up_xp = 7  # 基本レベルを設定
    elif type == 1:
        info_table_name = 'private_blog_user'
        xp_info_table_name = 'private_blog_user_xp'
        channel_insert_id_column = 'channel_insert_id'
        default_level_up_xp = 5  # 基本レベルを設定

    ##
    # 紐づけされているIDを各種取得
    ##
    search_main_info_insert_id = await db_reformat(await db_search('id', 'blog_main_info', f'category_id = {ctx.channel.category.id}'), 1)

    if search_main_info_insert_id:

        ##
        # 紐づけされているIDを各種取得
        ##
        search_main_info_insert_id = await db_reformat(
            await db_search('id', 'blog_main_info', f'category_id = {ctx.channel.category.id}'), 1)
        search_sub_info_insert_id = await db_reformat(
            await db_search('id', 'blog_sub_info', f'main_info_insert_id = {search_main_info_insert_id}'), 1)
        search_private_blog_user_insert_id = await db_reformat(
            await db_search('id', 'private_blog_user', f'channel_insert_id = {search_sub_info_insert_id}'), 1)

        # 投稿数をデータベースから取得
        search_info_table_number_of_posts = await db_reformat(await db_search('number_of_posts', f'{info_table_name}', f'{channel_insert_id_column} = {ctx.channel.id} AND number_of_posts >= 0'), 1)

        # 経験値をデータベースから取得
        db_get_exp = await db_search('xp', f'{xp_info_table_name}', f'channel_insert_id = {search_sub_info_insert_id} AND xp >= 0')
        reformat_xp = await db_reformat(db_get_exp, 1)
        # レベルをデータベースから取得
        db_get_level = await db_search('level', f'{xp_info_table_name}',
                                       f'channel_insert_id = {search_sub_info_insert_id} AND level >= 0')
        reformat_level = await db_reformat(db_get_level, 2)

        if reformat_level == 1:
            next_level_up_xp = float(default_level_up_xp * 1.1) + int(reformat_level * 2) / 2
        else:
            db_get_saved_levelup_xp = await db_search('saved_levelup_xp', f'{xp_info_table_name}',
                                                      f'channel_id = {ctx.channel.id} AND saved_levelup_xp IS NOT NULL')
            reformat_saved_levelup_xp = await db_reformat(db_get_saved_levelup_xp, 3)
            print(reformat_saved_levelup_xp)
            reformat_saved_levelup_xp = float(reformat_saved_levelup_xp)
            next_level_up_xp = float(reformat_saved_levelup_xp * 1.1) + int(reformat_level * 2) / 2
        rereformat_xp = int(reformat_xp) / 100
        rereformat_xp = str(rereformat_xp)
        rereformat_xp = rereformat_xp[:rereformat_xp.find('.')]

        next_level_up_xp = str(next_level_up_xp)
        next_level_up_xp = next_level_up_xp[:next_level_up_xp.find('.')]
        print(f'レベルアップに必要な経験値: {next_level_up_xp}\n現在の経験値{rereformat_xp}')
        if int(rereformat_xp) >= int(next_level_up_xp):
            val = (f"{next_level_up_xp}", f"{search_sub_info_insert_id}")
            await db_update(f'{xp_info_table_name}', 'saved_levelup_xp = %s WHERE channel_insert_id = %s', val)

            reformat_level = int(reformat_level) + 1
            embed = discord.Embed(
                title=f"レベルアップ!", color=0x8bc34a)
            embed.add_field(name=f"blogのレベルが{reformat_level}に上がりました!", value=f"今後もblogでのご活躍をご期待しています!",
                            inline=True)
            await ctx.channel.send(embed=embed)
            next_xp = '0'
        else:
            next_xp = int(reformat_xp) + + int(2) * 10
            print(f'今回の発言後のxp(小数) {next_xp / 100}\n今回の発言後のxp(整数) {next_xp}')
        next_number_of_posts = int(search_info_table_number_of_posts) + 1

        val = (f"{int(next_xp)}", f"{reformat_level}", f"{search_sub_info_insert_id}")
        await db_update(f'{xp_info_table_name}', 'xp = %s, level = %s WHERE channel_insert_id = %s', val)

        val = (f"{next_number_of_posts}", f"{ctx.channel.id}")
        await db_update(f'{info_table_name}', 'number_of_posts = %s WHERE channel_id = %s', val)


class BlogCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def blogcategory(self, ctx):
        await none_check_invoked_subcommand(ctx, 'このコマンドには引数が必要です')

    @blogcategory.command()
    async def register(self, ctx):
        search_server = session.query(BlogsServer).filter(BlogsServer.server_id == f'{ctx.guild.id}').first()

        if search_server is None:
            await db_manager.commit(BlogsServer(server_id=f'{ctx.guild.id}'))
        search_category = session.query(BlogsCategory).filter(and_(BlogsCategory.server_id == f'{ctx.guild.id}', BlogsCategory.category_id == f'{ctx.channel.category.id}')).first()
        if search_category is None:
            await db_manager.commit(BlogsCategory(server_id=f'{ctx.guild.id}', category_id=f'{ctx.channel.category.id}'))
            await embed_send(ctx, self.bot, 0, '成功', '登録に成功しました!')
        else:
            await embed_send(ctx, self.bot, 1, 'エラー', '既に登録されているカテゴリです')

    @blogcategory.command()
    async def deregister(self, ctx):
        db_search_category_id = await db_search('category_id', 'blog_main_info',
                                                f'category_id = {ctx.channel.category.id}')
        if len(db_search_category_id) == 0:
            sql = "INSERT INTO blog_main_info (server_id, category_id) VALUES (%s, %s)"
            val = (f"{ctx.guild.id}", f"{ctx.channel.category.id}")
            db_cursor.execute(sql, val)
            cnx.commit()
            await embed_send(ctx, self.bot, 1, 'エラー', '登録されていないカテゴリです')
        else:
            await db_delete('blog_main_info', 'category_id = %s', f'{ctx.channel.category.id}')
            await embed_send(ctx, self.bot, 0, '成功', 'カテゴリの解除に成功しました!')

    @commands.group()
    async def blog(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドには引数が必要です')

    @blog.command(name='setRole')
    async def _setrole(self, ctx, role: discord.Role):
        db_search_category_id = await db_search('category_id', 'blog_main_info',
                                                f'category_id = {ctx.channel.category.id}')
        if len(db_search_category_id) == 1:
            if ctx.author.guild_permissions.administrator:
                check_already_register = await db_search('role', 'blog_main_info',
                                                         f'server_id = {ctx.guild.id} AND role IS NOT NULL')
                if not check_already_register:
                    val = (f'{role.id}', f'{ctx.guild.id}')
                    await db_update('blog_main_info', 'role = %s WHERE server_id = %s', val)
                else:
                    print('kousinn')
            else:
                await embed_send(ctx, self.bot, 1, 'エラー', 'このコマンドには管理者権限が必要です')
        else:
            await embed_send(ctx, self.bot, 1, 'エラー',
                             f'登録されていないカテゴリです。\n```{bot_prefix}blogcategory register```を実行してください')

    @blog.command(name='register')
    async def _register(self, ctx):  # TODO:2020/11/13/ 自動生成を楽にするための機構を追加する
        search_blog_id, blog_server_id, blog_category_id, blog_channel_id = await blog_information(ctx)
        print(blog_category_id)
        if blog_category_id:  # 既にカテゴリが登録されてるか
            if blog_channel_id is None:  # 既にチャンネルが登録されてるか
                date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 登録日時用
                db_cursor.execute(f'INSERT INTO blogs (created_at) VALUES (\'{date}\')')
                sql_list = {
                    0: {
                        'table_name': 'blog_detail',
                        'sql': 'INSERT INTO blog_detail (blog_id, blog_channel, total_post) VALUES (%s, %s, %s)',
                        'val': (f'{search_blog_id}', f'{ctx.channel.id}', f'{ctx.author.id}', 0)
                    },
                    1: {
                        'table_name': 'blog_user_detail',
                        'sql': 'INSERT INTO blog_user_detail (blog_id, channel_id, user_id, total_post) VALUES (%s, %s, %s, %s)',
                        'val': (f'{search_blog_id}', f'{ctx.channel.id}', f'{ctx.author.id}', 0)
                    }
                }

                for main_key in sql_list.keys():
                    table_name = sql_list[main_key]['table_name']
                    sql = sql_list[main_key]['sql']
                    val = sql_list[main_key]['val']
                    print(sql % val)
                    await db_insert(sql, val)

                # await db_update('blog_detail', 'saved_levelup_xp = %s WHERE channel_id = %s', val)

                """


                member = await ctx.guild.fetch_member(ctx.author.id)
                role_id = await db_search('role', 'blog_main_info',
                                          f'server_id = {member.guild.id} AND role IS NOT NULL')

                if role_id:
                    reformat_role_id = await db_reformat(role_id, 2)
                    role = get(member.guild.roles, id=reformat_role_id)
                    await member.add_roles(role)
                    await embed_send(ctx, self.bot, 0, '成功', '登録に成功しました!')
                else:
                    await embed_send(ctx, self.bot, 0, '成功', '登録に成功しましたが権限が設定されていなかったため自動付与されていません!')"""
            else:
                await embed_send(ctx, self.bot, 1, 'エラー', '既に登録されているチャンネルです')
        else:
            await embed_send(ctx, self.bot, 1, 'エラー', '登録されていないカテゴリです')

    @blog.command(name='notice')
    async def _notice(self, ctx, on_off):
        member = await ctx.guild.fetch_member(ctx.author.id)
        role_id = await db_search('role', 'blog_main_info',
                                  f'server_id = {member.guild.id} AND role IS NOT NULL')
        reformat_role_id = await db_reformat(role_id, 2)
        role = get(member.guild.roles, id=reformat_role_id)

        async def default():
            for x in member.roles:
                if x.id == reformat_role_id:
                    print('hit')
                    hit = True
                    break
                else:
                    hit = None
            return hit

        if on_off == 'on':
            hit = await default()
            if hit is True:
                await embed_send(ctx, self.bot, 1, 'エラー', f'既にブログに関する通知は有効です!')
            else:
                await member.add_roles(role)
                await embed_send(ctx, self.bot, 0, '成功', f'ブログに関する通知を受け取るようになりました！')

        elif on_off == 'off':
            hit = await default()
            if hit is True:
                await member.remove_roles(role)
                await embed_send(ctx, self.bot, 0, '成功', f'ブログに関する通知を受け取らないようになりました！')
            else:
                await embed_send(ctx, self.bot, 1, 'エラー', f'既にブログに関する通知は無効です!')

    @blog.command(name='deregister')
    async def _deregister(self, ctx):
        db_search_channel_id = await db_search('channel_id', 'blog_sub_info', f'channel_id = {ctx.channel.id}')
        if len(db_search_channel_id) == 1:
            db_get_user_id = await db_search('user_id', 'blog_sub_info',
                                             f'channel_id = {ctx.channel.id} AND user_id = {ctx.author.id}')
            if len(db_get_user_id) == 1:
                await db_delete('blog_sub_info', 'channel_id = %s', f'{ctx.channel.id}')
                await db_delete('discord_blog_xp', 'channel_id = %s', f'{ctx.channel.id}')
                await embed_send(ctx, self.bot, 0, '成功', f'ブログの登録を解除しました\n{ctx.author.name}さん今までのご利用ありがとうございました!')
            else:
                await embed_send(ctx, self.bot, 1, 'エラー', f'所有または参加していないブログは削除できません!')
        else:
            await embed_send(ctx, self.bot, 1, 'エラー', 'ブログの登録がされていないチャンネルです')

    @blog.command(name='status')
    async def _status(self, ctx):
        db_search_channel_id = await db_search('channel_id', 'blog_sub_info', f'channel_id = {ctx.channel.id}')
        if len(db_search_channel_id) == 1:
            db_get_user_id = await db_search('user_id', 'blog_sub_info',
                                             f'channel_id = {ctx.channel.id} AND user_id IS NOT NULL')
            reformat_user_id = await db_reformat(db_get_user_id, 1)

            get_user_info = await self.bot.fetch_user(reformat_user_id)
            get_user_avatar_url = get_user_info.avatar_url
            get_blog_user_name = get_user_info.name

            db_get_number_of_posts = await db_search('number_of_posts', 'blog_sub_info',
                                                     f'channel_id = {ctx.channel.id} AND number_of_posts >= 0')
            reformat_number_of_posts = await db_reformat(db_get_number_of_posts, 1)

            # 1ちゃっとで0.2

            db_get_level = await db_search('level', 'discord_blog_xp', f'channel_id = {ctx.channel.id} AND level >= 0')
            for i in db_get_level:
                reformat_get_level = "".join(map(str, i))
            if 0 <= int(reformat_get_level) <= 2:
                emoji = '🌱'
            elif 2 <= int(reformat_get_level) <= 4:
                emoji = '🌸'
            elif 4 <= int(reformat_get_level) <= 8:
                emoji = '💎'
            elif 8 <= int(reformat_get_level) <= 16:
                emoji = '🌟'
            elif 16 <= int(reformat_get_level) <= 32:
                emoji = '👑'

            db_get_xp = await db_search('xp', 'discord_blog_xp', f'channel_id = {ctx.channel.id} AND xp IS NOT NULL')
            reformat_xp = await db_reformat(db_get_xp, 1)

            reformat_xp = int(reformat_xp) / 100
            reformat_level = int(reformat_get_level)
            default_level_up_xp = 5  # 基本レベルを設定
            if reformat_level == 1:
                next_level_up_xp = float(default_level_up_xp * 1.1) + int(reformat_level * 2) / 2
            else:
                db_get_saved_levelup_xp = await db_search('saved_levelup_xp', 'discord_blog_xp',
                                                          f'channel_id = {ctx.channel.id} AND saved_levelup_xp IS NOT NULL')
                reformat_saved_levelup_xp = await db_reformat(db_get_saved_levelup_xp, 3)
                next_level_up_xp = float(reformat_saved_levelup_xp * 1.1) + int(reformat_level * 2) / 2

            print(f'レベルアップに必要な経験値: {next_level_up_xp}\n現在の経験値{reformat_xp}')
            level_up = float(reformat_xp / next_level_up_xp * 100)
            level_up = str(level_up)
            level_up = level_up[:level_up.find('.')]
            embed = discord.Embed(
                title=f"{emoji}{get_blog_user_name}のブログステータス", color=0x8bc34a)
            embed.set_thumbnail(url=f"{get_user_avatar_url}")
            embed.add_field(
                name="投稿数", value=f"{reformat_number_of_posts}", inline=True)
            embed.add_field(name="blog称号", value=f"若葉", inline=False)
            embed.add_field(name="blog経験値", value=f"{reformat_xp}xp", inline=True)
            embed.add_field(name="blogレベル", value=f"{reformat_get_level}lv", inline=True)
            embed.add_field(name="blogのレベルアップまで", value=f"{level_up}/100%", inline=True)
            await ctx.channel.send(embed=embed)
        else:
            await embed_send(ctx, self.bot, 1, 'エラー', '登録されていないチャンネルです')

    @commands.group()
    async def bloguser(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドには引数が必要です')

    @bloguser.command(name='add')
    async def _add(self, ctx, arg):
        try:
            user = await self.bot.fetch_user(arg)
            await embed_send(ctx, self.bot, 0, '成功', 'エラー出てないです')
        except NotFound:
            await embed_send(ctx, self.bot, 1, 'エラー', '存在しないユーザーです')
        except HTTPException:
            await embed_send(ctx, self.bot, 1, 'エラー', 'ユーザーの取得に失敗しました')

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return
        if ctx.content != f'{bot_prefix}blog status':  # blog statusコマンドが投稿にカウントされないように
            """ 現在使用不可なのでコメントアウト
            if len(ctx.content) >= 3: 
                if len(ctx.content) >= 3:
                    myresult = await db_search('channel_id', 'blog_sub_info', f'channel_id = {ctx.channel.id}')
                    execution_user_id = f'{ctx.author.id}'
                    if len(myresult) >= 1:
                        print(f'{myresult}')
                        await blog_level_system(ctx, execution_user_id, 0)
                        await blog_level_system(ctx, execution_user_id, 1)
            """


def setup(bot):
    bot.add_cog(BlogCog(bot))

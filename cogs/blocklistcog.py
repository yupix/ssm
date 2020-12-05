import datetime

import discord
import typing
from discord import NotFound, HTTPException
from discord.ext import commands
from main import db_search, mycursor, mydb, db_reformat, db_delete, embed_send, db_insert, db_get_auto_increment, \
    bot_prefix, logger


async def blocklist_informations(ctx, user):
    search_blocklist_id = await db_reformat(await db_search('block_id', 'blocklist_user', f'server_id = {ctx.guild.id}'), 2)  # block_idを取得
    search_blocklist_server_id = await db_reformat(await db_search('server_id', 'blocklist_server', f'server_id = {ctx.guild.id}'), 2)  # server_idを取得
    search_blocklist_user_id = await db_reformat(await db_search('user_id', 'blocklist_user', f'user_id = {user.id}'), 2)  # user_idを取得

    return search_blocklist_id, search_blocklist_server_id, search_blocklist_user_id


async def blog_reaction(reaction, reformat_mode, user, msg, reformat_check_reaction):
    if reformat_mode == '0':
        embed_title = f'{user.name} さんをブロックリストに登録しました'
        embed_sub_title = 'サーバーに平和が訪れることを祈ります'

        cancele_embed_title = f'{user.name} さんのブロックリスト登録をキャンセルしました'
        cancele_embed_sub_title = '平和が一番ですよね♪'

    elif reformat_mode == '1':
        embed_title = f'{user.name} さんのブロックリストを解除しました'
        embed_sub_title = '問題が発生しないことを祈ります'

        cancele_embed_title = f'{user.name} さんのブロックリスト解除をキャンセルしました'
        cancele_embed_sub_title = '無理に解除する必要性はありません！'

    embed_color = 0x8bc34a
    if reaction.emoji == '✅':

        embed = discord.Embed(title=f'{embed_title}',
                              description=f'{embed_sub_title}', color=embed_color)
        await msg.edit(embed=embed)
        print(reformat_mode)
        if reformat_mode == '0':
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            mycursor.execute(f'INSERT INTO blocklists (created_at) VALUES (\'{date}\')')
            mydb.commit()

            reaction_id = await db_get_auto_increment() # auto_incrementのidを取得
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
            mycursor.execute(sql, adr)

            mydb.commit()

        await db_delete('reactions', 'message_id = %s', f'{msg.guild.id}')  # embedのデータを削除
    elif reaction.emoji == '✖':
        embed = discord.Embed(title=cancele_embed_title,
                              description=cancele_embed_sub_title, color=embed_color)
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
    async def register(self, ctx, mode, *args):
        if ctx.author.guild_permissions.administrator:
            search_server_id = await db_reformat(await db_search('server_id', 'blocklist_server', f'server_id = {ctx.guild.id}'), 2)
            if not search_server_id:  # サーバーIDが既に登録されてるか確認
                sql = "INSERT INTO blocklist_server (server_id) VALUES (%s)"
                val = (ctx.guild.id,)
                await db_insert(sql, val)
            search_settings_server_id = await db_reformat(
                await db_search('server_id', 'blocklist_settings', f'server_id = {ctx.guild.id}'), 2)

            if not search_settings_server_id:  # 既に設定が存在するか確認
                processing_mode_list = ['autokick', 'autoban', 'addrole', 'removerole']
                for check_mode in processing_mode_list:
                    if f'{mode}' == f'{check_mode}':  # 存在するmodeか確認
                        logger.debug('モードの確認に成功しました')
                        sql = "INSERT INTO blocklist_settings (server_id, mode) VALUES (%s, %s)"
                        val = (ctx.guild.id, f'{mode}')
                        if f'{mode}' == 'nonerole' or f'{mode}' == 'addrole':
                            role = self.bot.get_role(args[0])
                            print(role.id)
                            sql = "INSERT INTO blocklist_role (server_id, role_id) VALUES (%s, %s)"
                            val = (ctx.guild.id, role.id)
                            await db_insert(sql, val)
                        await db_insert(sql, val)
                        await embed_send(ctx, self.bot, 0, '成功', '設定を保存しました!')
                        break
                else:
                    await embed_send(ctx, self.bot, 1, 'エラー', '存在しないモードです')
            else:
                await embed_send(ctx, self.bot, 1, 'エラー', '既に設定が存在します')


    @blocklist.command()
    async def add(self, ctx, user_id, mode: typing.Optional[str] = None):
        if ctx.author.guild_permissions.administrator:
            db_search_server_id = await db_reformat(await db_search('server_id', 'blocklist_server', f'server_id = {ctx.guild.id}'), 2)
            if mode is not None:
                processing_mode_list = ['autokick', 'autoban', 'addrole', 'removerole']
                for check_mode in processing_mode_list:
                    if f'{mode}' == f'{check_mode}':  # 存在するmodeか確認
                        if db_search_server_id:  # サーバーIDが既に登録されてるか確認
                            try:
                                user = await self.bot.fetch_user(user_id)
                                search_blocklist_id, search_blocklist_server_id, search_blocklist_user_id = await blocklist_informations(ctx, user)
                                print(search_blocklist_id, search_blocklist_server_id, search_blocklist_user_id)
                                if not search_blocklist_user_id:
                                    embed = discord.Embed(title=f"{user.name} をブロックリストに登録しますか？",
                                                          description="怒りに我を忘れていないかもう一度冷静になって確認してみましょう\n問題が無いようなら✅を押してください。",
                                                          color=0xffc629)
                                    msg = await ctx.send(embed=embed)
                                    await msg.add_reaction('✅')
                                    await msg.add_reaction('✖')

                                    sql = "INSERT INTO reactions (message_id) VALUES (%s)"
                                    val = (msg.id,)
                                    await db_insert(sql, val)

                                    search_reaction_id = await db_reformat(await db_search('id', 'reactions', f'message_id = {msg.id}'), 2)
                                    sql = "INSERT INTO blocklist_reaction (reaction_id, server_id, channel_id, user_id, command, mode, block_mode) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                                    val = (search_reaction_id, msg.guild.id, msg.channel.id, user.id, 'blocklist', 0, f'{mode}')
                                    await db_insert(sql, val)

                                else:
                                    await embed_send(ctx, self.bot, 1, 'エラー', '既に登録されているユーザーです')
                            except NotFound:
                                await embed_send(ctx, self.bot, 1, 'エラー', '存在しないユーザーです')
                            except HTTPException:
                                await embed_send(ctx, self.bot, 1, 'エラー', '取得時にエラーが発生しました')
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
                search_blocklist_id, search_blocklist_server_id, search_blocklist_user_id = await blocklist_informations(ctx, user)

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
            #search_datatime = await db_reformat(await db_search('user_id', 'blocklists', f'id = {ctx.guild.id}'), 2)

            for i in range(len(search_block_id)):

                print(search_block_id)
                block_id = await db_reformat(f'{search_block_id[-i]}', 1)
                user_id = await db_reformat(f'{search_user_id[-i]}', 1)
                print(f'{block_id}', f'{user_id}')
                print(''.join((2), (1)))

        else:
            await ctx.send('このコマンドには管理者必須やで')


def setup(bot):
    bot.add_cog(BlocklistCog(bot))

import discord
from discord import NotFound, HTTPException
from discord.ext import commands

from main import db_search, mycursor, mydb, db_reformat, db_delete, embed_send


class BlocklistCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def blocklist(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('this command is sub option required')

    @blocklist.command()
    async def register(self, ctx, role: discord.Role):
        if ctx.author.guild_permissions.administrator:
            check_alredy_register = await db_search('server_id', 'discord_main_block_list',
                                                    f'server_id = {ctx.guild.id}')
            if not check_alredy_register:
                sql = "INSERT INTO discord_main_block_list (server_id, role) VALUES (%s, %s)"
                val = (ctx.guild.id, role.id)
                mycursor.execute(sql, val)

                mydb.commit()
            else:
                await ctx.send('既に登録されてるよ')

    @blocklist.command()
    async def add(self, ctx, user_id):
        if ctx.author.guild_permissions.administrator:

            try:
                user = await self.bot.fetch_user(user_id)
                check_already_register = await db_search('user_id', 'discord_sub_block_list',
                                                         f'server_id = {ctx.guild.id} AND user_id = {user.id}')
                if not check_already_register:
                    print('koko')
                    print('koko2')
                    embed = discord.Embed(title=f"{user.name} をブロックリストに登録しますか？",
                                          description="怒りに我を忘れていないかもう一度冷静になって確認してみましょう\n問題が無いようなら✅を押してください。",
                                          color=0xffc629)
                    msg = await ctx.send(embed=embed)
                    await msg.add_reaction('✅')
                    await msg.add_reaction('✖')

                    sql = "INSERT INTO discord_blocklist_reaction (channel_id, message_id, user_id, type) VALUES (%s, %s, %s, %s)"
                    val = (msg.channel.id, msg.id, user.id, 0)
                    mycursor.execute(sql, val)

                    mydb.commit()
                else:
                    await embed_send(ctx, self.bot, 1, 'エラー', '既に登録されているユーザーです')
            except NotFound:
                await embed_send(ctx, self.bot, 1, 'エラー', '存在しないユーザーです')
            except HTTPException:
                await embed_send(ctx, self.bot, 1, 'エラー', '取得時にエラーが発生しました')

    @blocklist.command()
    async def remove(self, ctx, user_id):
        if ctx.author.guild_permissions.administrator:
            try:
                user = await self.bot.fetch_user(user_id)
                check_register = await db_search('user_id', 'discord_sub_block_list',
                                                 f'server_id = {ctx.guild.id} AND user_id = {user.id}')
                if check_register:
                    embed = discord.Embed(title=f"{user.name} をブロックリストから解除しますか？",
                                          description="最後にもう一度、本当に解除しても問題ないですか？\n問題が無いようなら✅を押してください。", color=0xffc629)
                    msg = await ctx.send(embed=embed)
                    await msg.add_reaction('✅')
                    await msg.add_reaction('✖')

                    sql = "INSERT INTO discord_blocklist_reaction (channel_id, message_id, user_id, type) VALUES (%s, %s, %s, %s)"
                    val = (msg.channel.id, msg.id, user.id, 1)
                    mycursor.execute(sql, val)

                    mydb.commit()
                else:
                    await embed_send(ctx, self.bot, 1, 'エラー', '登録されていないユーザーです')
            except NotFound:
                await embed_send(ctx, self.bot, 1, 'エラー', '存在しないユーザーです')
            except HTTPException:
                await embed_send(ctx, self.bot, 1, 'エラー', '取得時にエラーが発生しました')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        if user == self.bot.user:
            return
        emoji = reaction.emoji
        message_id = reaction.message.id
        channel_id = reaction.message.channel.id
        check_reaction = await db_search('message_id', 'discord_blocklist_reaction', f'message_id = {message_id}')
        reformat_check_reaction = await db_reformat(check_reaction, 1)
        if check_reaction:
            check_channel = await db_search('channel_id', 'discord_blocklist_reaction', f'channel_id = {channel_id}')
            reformat_channel = await db_reformat(check_channel, 2)

            check_user = await db_search('user_id', 'discord_blocklist_reaction',
                                         f'channel_id = {channel_id} AND user_id IS NOT NULL')
            reformat_user = await db_reformat(check_user, 1)
            user = await self.bot.fetch_user(reformat_user)

            check_type = await db_search('type', 'discord_blocklist_reaction',
                                         f'channel_id = {channel_id} AND type IS NOT NULL')
            reformat_type = await db_reformat(check_type, 2)

            channel = reaction.message.guild.get_channel(reformat_channel)
            msg = await channel.fetch_message(message_id)
            if reformat_type == 0:
                embed_title = f'{user.name} さんをブロックリストに登録しました'
                embed_subtitle = 'サーバーに平和が訪れることを祈ります'
                embed_color = 0x8bc34a

                cancel_embed_title = f'{user.name} さんのブロックリスト登録をキャンセルしました'
                cancel_embed_subtitle = '平和が一番ですよね♪'
                cancel_embed_color = 0x8bc34a

            elif reformat_type == 1:
                embed_title = f'{user.name} さんのブロックリストを解除しました'
                embed_subtitle = f'{user.name} さんが再度参加が可能になりました'
                embed_color = 0x8bc34a

                cancel_embed_title = f'{user.name} さんブロックリスト解除をキャンセルしました'
                cancel_embed_subtitle = '無理に解除する必要性はありません！'
                cancel_embed_color = 0x8bc34a

            if reaction.emoji == '✅':

                embed = discord.Embed(title=embed_title,
                                      description=embed_subtitle, color=embed_color)
                await msg.edit(embed=embed)
                if reformat_type == 0:
                    sql = "INSERT INTO discord_sub_block_list (server_id, user_id, count) VALUES (%s, %s, %s)"
                    val = (msg.guild.id, user.id, 0)
                    mycursor.execute(sql, val)

                    mydb.commit()
                elif reformat_type == 1:
                    sql = f'DELETE FROM discord_sub_block_list WHERE server_id = %s AND user_id = %s'
                    adr = (msg.guild.id, user.id,)
                    mycursor.execute(sql, adr)

                    mydb.commit()

                await db_delete('discord_blocklist_reaction', 'message_id = %s',
                                f'{reformat_check_reaction}')  # embedのデータを削除
            elif reaction.emoji == '✖':
                embed = discord.Embed(title=cancel_embed_title,
                                      description=cancel_embed_subtitle, color=cancel_embed_color)
                await msg.edit(embed=embed)
                await db_delete('discord_blocklist_reaction', 'message_id = %s', f'{reformat_check_reaction}')


def setup(bot):
    bot.add_cog(BlocklistCog(bot))

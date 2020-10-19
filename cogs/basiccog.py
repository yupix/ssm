import discord
from discord.ext import commands
from discord.utils import get

from cogs.blocklistcog import blog_reaction
from cogs.modpackcog import modpack_reaction
from main import db_search, db_reformat, mycursor, mydb, db_update, json_load, bot_prefix

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

                mycursor.execute(sql, val)
                mydb.commit()
            else:
                msg.channel.send('既に登録されています')



            mydb.commit()
"""


class BasicCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.channel.send(f'ping: {round(self.bot.latency * 1000)}ms ')

    """利用規約同意のデータが追加されたあとも認識しないため一時的にコメントアウト
    @commands.command()
    async def agree(self, ctx):
        embed = discord.Embed(title='利用規約', description='この利用規約はゆぴ(作者)がいついかなる時でも変更する権利を保留することを予めご理解ください。', color=0x0f9dcc)
        embed.add_field(name='最終更新日', value=f'2020/10/05', inline=False)
        embed.add_field(name='概要', value=f'この利用規約は本Botを使用する上での注意事項を含んでいるため最後まで読むことを推奨します', inline=False)
        embed.add_field(name='1.個人情報に関して', value=f'本Botではすべての機能に個人を特定するような機能はついておりません。また、それを補助するような機能などもございません。', inline=True)
        embed.add_field(name='2.保存する情報について', value=f'本Botを使用する上で以下の情報を取得することがあります。```- サーバーID\n- チャンネルID\n- ユーザーID\n- 発言数(一部のみ)```', inline=True)
        embed.add_field(name='3.保存した情報の取り扱いについて', value=f'本BotではAPIとして登録したサーバーなどが一覧で見れるようなもの作成する予定がある為、個人単位での設定により非公開にすることが可能です(デフォルトは非公開)。', inline=False)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('✅')
        await msg.add_reaction('✖')
        sql = "INSERT INTO discord_reaction (channel_id, message_id, user_id, command, mode, original_message_id) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (msg.channel.id, msg.id, ctx.author.id, 'basic', 0, ctx.message.id)

        mycursor.execute(sql, val)

        mydb.commit()
    """
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        print(member.id)
        check_block_list = await db_search('user_id', 'discord_sub_block_list',
                                           f'server_id = {member.guild.id} AND user_id = {member.id}')
        if check_block_list:
            print('ブロックユーザーです')
        else:
            role_id = await db_search('role', 'discord_main_block_list',
                                      f'server_id = {member.guild.id} AND role IS NOT NULL')
            reformat_role_id = await db_reformat(role_id, 2)
            role = get(member.guild.roles, id=reformat_role_id)
            print(f'{role.name}')
            await member.add_roles(role)

        # reformat_check_reaction = await db_reformat(check_reaction, 1)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        if user == self.bot.user:
            return
        emoji = reaction.emoji
        reaction_message_id = reaction.message.id  # リアクションが付いたメッセージID
        reaction_channel_id = reaction.message.channel.id  # リアクションが付いたメッセージのあるチャンネルID

        check_reaction = await db_search('message_id', 'discord_reaction', f'message_id = {reaction_message_id}')

        if check_reaction:
            reformat_check_reaction = await db_reformat(check_reaction, 1)
            check_channel = await db_search('channel_id', 'discord_reaction', f'channel_id = {reaction_channel_id}')
            reformat_channel = await db_reformat(check_channel, 2)

            check_user = await db_search('user_id', 'discord_reaction',
                                         f'channel_id = {reaction_channel_id} AND user_id IS NOT NULL')
            reformat_user = await db_reformat(check_user, 1)
            user = await self.bot.fetch_user(reformat_user)

            check_command = await db_search('command', 'discord_reaction',
                                            f'channel_id = {reaction_channel_id} AND message_id = {reaction_message_id} AND command IS NOT NULL')
            reformat_command = await db_reformat(check_command, 1)

            check_original_message_id = await db_search('original_message_id', 'discord_reaction',
                                            f'channel_id = {reaction_channel_id} AND message_id = {reaction_message_id} AND original_message_id IS NOT NULL')
            reformat_original_message_id = await db_reformat(check_original_message_id, 1)

            channel = reaction.message.guild.get_channel(reformat_channel)

            ogl_msg = await channel.fetch_message(reformat_original_message_id)
            msg = await channel.fetch_message(reaction_message_id)
            check_mode = await db_search('mode', 'discord_reaction',
                                         f'channel_id = {reaction_channel_id} AND message_id = {reaction_message_id} AND mode IS NOT NULL')
            reformat_mode = await db_reformat(check_mode, 1)

            print(f'見つかったチャンネルID: {reformat_channel}\n'
                  f'見つかったユーザーID: {reformat_user}\n'
                  f'見つかったコマンド: {reformat_command}\n'
                  f'モード: {reformat_mode}\n'
                  f'付けられた絵文字: {emoji}')

            if reformat_command == 'blocklist':
                await blog_reaction(reaction, reformat_mode, user, msg, reformat_check_reaction)
            elif reformat_command == 'modpack':
                await modpack_reaction(reaction, reformat_mode, user, msg, reformat_check_reaction, ogl_msg)
            # elif reformat_command == 'basic':
                # await basic_reaction(reaction, reformat_mode, user, msg, reformat_check_reaction, ogl_msg)


def setup(bot):
    bot.add_cog(BasicCog(bot))

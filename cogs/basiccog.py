import discord
from discord.ext import commands
from discord.utils import get

from cogs.blocklistcog import blog_reaction
from cogs.modpackcog import modpack_reaction
from main import db_search, db_reformat


class BasicCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.channel.send(f'ping: {round(self.bot.latency * 1000)}ms ')

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

def setup(bot):
    bot.add_cog(BasicCog(bot))

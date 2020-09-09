import discord
from discord.ext import commands
from discord.utils import get

from main import db_search, db_reformat


class BasicCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await ctx.send('test!')

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        print(member.id)
        check_block_list = await db_search('user_id', 'discord_sub_block_list', f'server_id = {member.guild.id} AND user_id = {member.id}')
        if check_block_list:
            print('ブロックユーザーです')
        else:
            role_id = await db_search('role', 'discord_main_block_list', f'server_id = {member.guild.id} AND role IS NOT NULL')
            reformat_role_id = await db_reformat(role_id, 2)
            role = get(member.guild.roles, id=reformat_role_id)
            print(f'{role.name}')
            await member.add_roles(role)

        #reformat_check_reaction = await db_reformat(check_reaction, 1)


def setup(bot):
    bot.add_cog(BasicCog(bot))

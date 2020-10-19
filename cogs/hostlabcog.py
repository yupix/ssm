from discord.ext import commands

from main import check_url, db_reformat, embed_send


class HostlabCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def hostlab(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドには引数が必要です')

    @hostlab.command()
    async def status(self, ctx, *repo_name):
        if len(repo_name) != 0:
            reformat_repo_name = await db_reformat(repo_name, 1)
        else:
            await ctx.send('引数が不足しています')
            return 1
        if reformat_repo_name.upper() == 'akari'.upper():
            http_status = await check_url('https://lab.akarinext.org')
        elif reformat_repo_name.upper() == 'akirin'.upper():
            http_status = await check_url('https://lab.akirin.xyz')

        if http_status == 0:
            await embed_send(ctx, self.bot, 0, f'{reformat_repo_name.upper()}Repository Status', '問題なく稼働中です')


def setup(bot):
    bot.add_cog(HostlabCog(bot))

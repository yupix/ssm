from discord.ext import commands
from discord.ext import commands

from main import logger


class LevelCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def grobal(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドには引数が必要です')

    @grobal.command(name='profile')
    async def profile(self, ctx, arg):
        logger.debug('作成中')

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return
        logger.debug('作成中')


def setup(bot):
    bot.add_cog(LevelCog(bot))

import asyncio
import math
import re

import discord
import typing

import mysql
from discord.ext import commands

from main import logger, Output_wav_name, check_variable, db_insert, db_reformat, db_search, embed_send


class Pso2Cog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def pso2(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドには引数が必要です')

    @pso2.command(name='grinder_m')
    async def _grinder_m(self, ctx, meseta_number: typing.Optional[int] = 10000):
        """
        グラインダー1: 500
        エクスキューブ1: 30
        一度に交換できる数: 33
        """
        grinder_one_plaices = 500
        trade_excube_max = 30
        required_grinder_number = (math.floor(meseta_number / grinder_one_plaices))
        calculate_excube = (math.floor(meseta_number / grinder_one_plaices / trade_excube_max))
        embed = discord.Embed(title="エクスキューブ金策補助",
                              description="指定した目標メセタに必要なエクスキューブ数を表示します。小数点は切り捨てされているため正確ではない可能性があります。")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/693570078926700587/784656064879919144/E382A8E382AFE382B9E382ADE383A5E383BCE383962E706E67.png")
        embed.add_field(name="目標メセタ", value="{:,}".format(meseta_number) + 'メセタ', inline=True)
        embed.add_field(name="必要なグラインダー数", value="{:,}".format(required_grinder_number) + '個', inline=True)
        embed.add_field(name="必要なエクスキューブ数", value="{:,}".format(calculate_excube) + '個', inline=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Pso2Cog(bot))

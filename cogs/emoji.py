import asyncio
import re

import discord
import typing

import mysql
from discord.ext import commands

from main import logger, Output_wav_name, check_variable, db_insert, db_reformat, db_search, embed_send


class EmojiCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def emoji(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドには引数が必要です')

    @emoji.command(name='add')
    async def _add(self, ctx, emoji_name: typing.Optional[str] = None, emoji_url: typing.Optional[str] = None):
        await ctx.send('test')

    @emoji.command(name='list')
    async def _list(self, ctx, option: typing.Optional[str] = None):
        emojis = ''
        emoji_list = ''
        emoji_list_id = ''
        embed = discord.Embed(color=0x859fff)
        for i in range(len(ctx.message.guild.emojis)):
            if len(embed) < 1800:
                #emojis += str(ctx.message.guild.emojis[i])
                #emoji_list_id += str(ctx.message.guild.emojis[i].id) + '\n'
                if option == '--all':
                    embed.add_field(name=f"" + str(ctx.message.guild.emojis[i]) + ' `:' + str(ctx.message.guild.emojis[i].name) + ':`' + '\\' +  str(ctx.message.guild.emojis[i]).replace('_', '\_'), value=f"" + '`' + str(ctx.message.guild.emojis[i].url) + '`', inline=True)
                else:
                    embed.add_field(name=f"" + str(ctx.message.guild.emojis[i]) + ' `:' + str(ctx.message.guild.emojis[i].name) + ':`', value=f"" + '`' + str(ctx.message.guild.emojis[i].url) + '`', inline=True)
                #emoji_list += str(ctx.message.guild.emojis[i]) + ' `' + str(ctx.message.guild.emojis[i].name) + '` ' + '\\' +  str(ctx.message.guild.emojis[i]).replace('_', '\_') + ' `' + str(ctx.message.guild.emojis[i].url) + '`' + '\n'
            else:
                await ctx.send(embed=embed)
                embed = discord.Embed(color=0x859fff)
                #await ctx.send(emoji_list)
                #emoji_list = ''
        await ctx.send(embed=embed)
        #await ctx.send(emoji_list)
        #await ctx.send(emoji_list_id)
        #await ctx.send(ctx.message.guild.emojis)



def setup(bot):
    bot.add_cog(EmojiCog(bot))

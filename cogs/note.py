import asyncio
import re

import discord
import typing

import mysql
from discord.ext import commands

from main import logger, Output_wav_name, check_variable, db_insert, db_reformat, db_search, embed_send


class NoteCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def note(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドには引数が必要です')

    @note.command(name='add')
    async def _add(self, ctx, note, use_category=None, category_name=None):
        if re.findall('<@(.*?)>', f'{note}') or re.findall('<@(.*?)>', f'{category_name}'):
            await ctx.send('メンションは使用することができません')
            return
        logger.debug(note)
        variable = await check_variable(note, 'addを使用するにはnoteをつける必要性があります', ctx)
        if variable == 0:
            sql = "INSERT IGNORE INTO notes (server_id) VALUES (%s)"
            val = (f'{ctx.guild.id}',)
            await db_insert(sql, val)
            if use_category and use_category == '-c':
                logger.debug(f'オプションが付与されています: {category_name}')
                search_category_name = await db_search(custom=f'category_name from notes_category where category_name = \'{category_name}\'')

                if not search_category_name:
                    sql = "INSERT INTO notes_category (category_name) VALUES (%s)"
                    val = f'{category_name}',
                    await db_insert(sql, val)

                sql = "INSERT INTO notes_detail (server_id, user_id, content, category_name) VALUES (%s, %s, %s, %s)"
                val = (f'{ctx.guild.id}', f'{ctx.author.id}', f'{note}', f'{category_name}')
            else:
                sql = "INSERT INTO notes_detail (server_id, user_id, content) VALUES (%s, %s, %s)"
                val = (f'{ctx.guild.id}', f'{ctx.author.id}', f'{note}')
            try:
                await db_insert(sql, val)
            except mysql.connector.Error as err:
                if err.errno == 1062:
                    await ctx.send('重複した内容のnoteは追加できません')

    @note.command(name='remove')
    async def _remove(self, ctx, note: typing.Optional[str] = None):
        await check_variable(note, '削除するnoteのIDを入力してください', ctx)

    @note.command(name='list')
    async def _list(self, ctx, note_author: typing.Optional[discord.User] = 'me', use_category=None, category_name=None):
        if note_author == 'me':
            note_author = ctx.author
        if use_category == '-c':
            search_reaction_id = await db_search('content', 'notes_detail', f'user_id = {note_author.id} AND content IS NOT NULL AND category_name = \'{category_name}\'')
        else:
            search_reaction_id = await db_search('content', 'notes_detail', f'user_id = {note_author.id} AND content IS NOT NULL AND category_name IS NULL')
        note_list = ''
        embed = discord.Embed(color=0x859fff)
        for i in search_reaction_id:
            custom_message = ''
            for emoji in re.finditer('e!(.*?)!e', f'{search_reaction_id}'):
                base_message = re.sub("\(|\)|\'", "", f'{i}').replace(',', '\n')
                for n in emoji.groups():  # emoji
                    check_emoji_type = re.sub("\\D", "", n)
                    if len(str(check_emoji_type)) == 18:
                        get_emoji = self.bot.get_emoji(int(check_emoji_type))
                        print(get_emoji)
                    else:
                        get_emoji = discord.utils.get(ctx.guild.emojis, name=f'{n}'.replace(':', ''))
                    if len(custom_message) == 0:
                        custom_message = base_message.replace(',', '\n').replace(f'e!{n}!e', f'{get_emoji}')
                    else:
                        custom_message = custom_message.replace(',', '\n').replace(f'e!{n}!e', f'{get_emoji}')
            if 'emoji' not in locals():
                custom_message = await db_reformat(i, 1) + '\n'
            print(custom_message)
            r_custom_message = await db_reformat(i, 1)
            search_notes_id = await db_reformat(await db_search('id', 'notes_detail', f'user_id = {note_author.id} '
                                                                    f'AND content = \'{r_custom_message}\''), 2)
            embed.add_field(name=f"ID: {search_notes_id}", value=f"{custom_message}", inline=True)
            #note_list += custom_message
        if not embed:
            await embed_send(ctx, self.bot, 0, 'INFO', 'ノートは空のようです', 0x859fff)
            return

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(NoteCog(bot))

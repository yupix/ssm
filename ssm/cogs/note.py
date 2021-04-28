import re
import typing
from logging import getLogger

import discord
from discord.ext import commands
from sqlalchemy import text, and_

from ssm import session
from ssm.base import db_manager
from ssm.main import check_variable, embed_send, check_args
from ssm.sql.models.note import NotesCategory, NotesDetail, NotesUser

logger = getLogger('main').getChild('note')


class NoteCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def note(self, ctx):
        if ctx.invoked_subcommand is None:
            logger.debug('test')
            await ctx.send('このコマンドには引数が必要です')

    @note.command(name='add')
    async def _add(self, ctx, note, use_category=None, category_name=None):
        if re.findall('<@(.*?)>', f'{note}') or re.findall('<@(.*?)>', f'{category_name}'):
            await ctx.send('メンションは使用することができません')
            return
        logger.debug(note)
        variable = await check_variable(note, 'addを使用するにはnoteをつける必要性があります', ctx)
        if variable == 0:
            await db_manager.commit(NotesUser(user_id=ctx.author.id))

            if use_category is not None and use_category == '-c' and category_name is not None:
                logger.debug(f'カテゴリ「{category_name}」が指定されました')
            else:
                category_name = 'デフォルト'
            search_category_name = session.query(NotesCategory).filter(NotesCategory.category_name == f'{category_name}').all()
            if len(search_category_name) == 0:
                logger.debug(f'カテゴリ「{category_name}」が存在しないため作成します')
                await db_manager.commit(NotesCategory(category_name=f'{category_name}'))
            add_note_result = await db_manager.commit(NotesDetail(user_id=f'{ctx.author.id}', content=f'{note}', category_name=f'{category_name}'), True)
            if add_note_result != 'IntegrityError':
                embed = discord.Embed(title="ノートの登録に成功しました", description="このメッセージは10秒後に自動で削除されます", color=0xff7e70)
                embed.add_field(name="id", value=f"{add_note_result}", inline=True)
                embed.add_field(name="ノート内容", value=f"{note}", inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send('重複した内容のnoteは追加できません')

    @note.command(name='remove')
    async def _remove(self, ctx, note_id: typing.Optional[int] = None):
        notes = session.query(NotesDetail).filter(and_(NotesDetail.user_id == f'{ctx.author.id}', NotesDetail.id == f'{note_id}')).first()

        if notes is None:
            await ctx.send('存在しないidです')
            return
        if notes.user_id == ctx.author.id:
            await db_manager.commit(session.query(NotesDetail).filter(and_(NotesDetail.user_id == f'{ctx.author.id}', NotesDetail.id == f'{note_id}')).delete(), commit_type='delete')

    @note.command(name='list')
    async def _list(self, ctx, note_author: typing.Optional[discord.User] = 'me', *, args: check_args = None):

        if note_author == 'me':
            note_author = ctx.author  # ユーザー指定
        if args is not None:
            if type(args) is not dict:
                await ctx.send(f'{args[1]}')
                return
            else:
                if '-c' in args and args.get('-c') is not None:
                    category_name = args.get('-c')
                    notes = session.query(NotesDetail).filter(and_(NotesDetail.user_id == f'{ctx.author.id}', NotesDetail.category_name == f'{category_name}')).all()
                if '--type' in args and 'category' == args.get('--type'):
                    notes = session.query(NotesDetail).filter(NotesDetail.user_id == f'{ctx.author.id}').all()
        else:
            category_name = 'デフォルト'
            notes = session.query(NotesDetail).filter(and_(NotesDetail.user_id == f'{ctx.author.id}', NotesDetail.category_name == f'{category_name}')).all()

        note_list = ''
        embed = discord.Embed(color=0x859fff)
        for i in notes:
            custom_message = ''
            for emoji in re.finditer('e!(.*?)!e', f'{i.content}'):
                base_message = re.sub("\(|\)|\'", "", f'{i.content}').replace(',', '\n')
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
                custom_message = i.content + '\n'
            else:
                del emoji
            print(custom_message)
            r_custom_message = i.content
            embed.add_field(name=f"ID: {i.id}", value=f"{custom_message}", inline=True)
        if not embed:
            await embed_send(ctx, self.bot, 0, 'INFO', 'ノートは空のようです', 0x859fff)
            return

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(NoteCog(bot))

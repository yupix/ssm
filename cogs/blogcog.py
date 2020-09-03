import discord
from discord.ext import commands

from main import mycursor, mydb, embed_send, db_search, db_delete, db_insert


class BlogCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def blogcategory(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドには引数が必要です')

    @blogcategory.command()
    async def register(self, ctx):
        myresult = await db_search('category_id', 'discord_main_blog', f'category_id = {ctx.channel.category.id}')
        if len(myresult) == 0:
            sql = "INSERT INTO discord_main_blog (server_id, category_id) VALUES (%s, %s)"
            val = (f"{ctx.guild.id}", f"{ctx.channel.category.id}")
            mycursor.execute(sql, val)
            mydb.commit()
            await embed_send(ctx, self.bot, 0, '成功', '登録に成功しました!')
        else:
            await embed_send(ctx, self.bot, 1, 'エラー', '既に登録されているカテゴリです')

    @blogcategory.command()
    async def unregister(self, ctx):
        myresult = await db_search('category_id', 'discord_main_blog', f'category_id = {ctx.channel.category.id}')
        if len(myresult) == 0:
            sql = "INSERT INTO discord_main_blog (server_id, category_id) VALUES (%s, %s)"
            val = (f"{ctx.guild.id}", f"{ctx.channel.category.id}")
            mycursor.execute(sql, val)
            mydb.commit()
            await embed_send(ctx, self.bot, 1, 'エラー', '登録されていないカテゴリです')
        else:
            await db_delete('discord_main_blog', 'category_id = %s', f'{ctx.channel.category.id}')
            await embed_send(ctx, self.bot, 0, '成功', 'カテゴリの解除に成功しました!')

    @commands.group()
    async def blog(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドには引数が必要です')

    @blog.command()
    async def register(self, ctx):
        myresult = await db_search('channel_id', 'discord_sub_blog', f'category_id = {ctx.channel.category.id} AND channel_id = {ctx.channel.id}')
        if len(myresult) == 0:
            db_insert('discord_sub_blog')
            await embed_send(ctx, self.bot, 0, '成功', '登録に成功しました!')
        else:
            await embed_send(ctx, self.bot, 1, 'エラー', '既に登録されているカテゴリです')

    @blog.command()
    async def unregister(self, ctx):
        myresult = await db_search('category_id', 'discord_main_blog', f'category_id = {ctx.channel.category.id}')
        if len(myresult) == 0:
            sql = "INSERT INTO discord_main_blog (server_id, category_id) VALUES (%s, %s)"
            val = (f"{ctx.guild.id}", f"{ctx.channel.category.id}")
            mycursor.execute(sql, val)
            mydb.commit()
            await embed_send(ctx, self.bot, 1, 'エラー', '登録されていないカテゴリです')
        else:
            await db_delete('discord_main_blog', 'category_id = %s', f'{ctx.channel.category.id}')
            await embed_send(ctx, self.bot, 0, '成功', 'カテゴリの解除に成功しました!')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.content == 'こんにちは':
            await message.channel.send(f'{message.author.name}さんこんにちは！')


def setup(bot):
    bot.add_cog(BlogCog(bot))

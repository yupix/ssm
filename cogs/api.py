import discord
from discord.ext import commands


class ApiCog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	async def check_operator(self, guild_id, user_id):
		"""指定したギルドで指定したユーザーがオペレーター権限を持っているかをBooleanで返します"""
		await self.bot.fetch_user(user_id)
		return 'test'



def setup(bot):
	bot.add_cog(ApiCog(bot))

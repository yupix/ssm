import discord
from discord.ext import commands


class TestCog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def what(self, ctx, what):
		await ctx.send(f'{what}とはなんですか?')

	@commands.group()
	async def role(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('this command is sub option required')

	@role.command()
	async def add(self, ctx, member: discord.Member, role: discord.Role):
		await member.add_roles(role)

	@role.command()
	async def remove(self, ctx, member: discord.Member, role: discord.Role):
		await member.remove_roles(role)


def setup(bot):
	bot.add_cog(TestCog(bot))

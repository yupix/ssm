import asyncio

import discord
from discord.ext import commands

from main import logger, Output_wav_name
from modules.voice_generator import create_wave


class ReadCog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True, name='status')
	async def status(self, ctx):
		#print(member)
		#member = discord.Member(ctx.author.id)
		member = await ctx.guild.fetch_member(ctx.author.id)
		print(member.status)

	@commands.command()
	async def join(self, ctx):
		member = await ctx.guild.fetch_member(ctx.author.id)
		print(member.status)

		vc = ctx.author.voice.channel
		logger.debug(f'ボイスチャンネル {vc} に参加しました')
		create_wave(f'こんにちは! 読み上げを開始します。')
		source = discord.FFmpegPCMAudio(f"{Output_wav_name}")
		try:
			await vc.connect()
			await asyncio.sleep(3)
			ctx.guild.voice_client.play(source)
		except discord.ClientException:
			create_wave(f'既に参加しています')

			source = discord.FFmpegPCMAudio(f"{Output_wav_name}")
			ctx.guild.voice_client.play(source)

	@commands.command()
	async def leave(self, ctx):
		create_wave(f'読み上げを終了します。お疲れ様でした。')
		source = discord.FFmpegPCMAudio(f"{Output_wav_name}")
		ctx.guild.voice_client.play(source)
		await asyncio.sleep(4)
		await ctx.voice_client.disconnect()
		logger.debug(f'ボイスチャンネル {ctx.voice_client.name} から退出しました')


def setup(bot):
	bot.add_cog(ReadCog(bot))

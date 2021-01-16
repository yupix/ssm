import discord
import feedparser
from discord.ext import commands
from main import check_args, logger


class RssCog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Command
	async def rss(self, ctx, rss_url, *, args: check_args = None):
		if args is not None:
			if type(args) is not dict:
				await ctx.send(f'{args[1]}')
				return
			else:
				if '--max' in args:
					logger.debug('test')
					max_get_number = args.get('--max')
		else:
			max_get_number = None

		d = feedparser.parse(rss_url)
		embed=discord.Embed(title="取得したRSS情報")
		for i, entry in enumerate(d.entries):
			logger.debug(i)
			if max_get_number is not None:
				if f'{max_get_number}' != f'{i}':
					if len(embed) < 1800:
						embed.add_field(name=f"{entry.title}", value=f"{entry.link}", inline=True)
					else:
						await ctx.send(embed=embed)
						embed=discord.Embed(title="取得したRSS情報")
				else:
					await ctx.send(embed=embed)
					return
			else:
				if len(embed) < 1800:
						embed.add_field(name=f"{entry.title}", value=f"{entry.link}", inline=True)
				else:
					await ctx.send(embed=embed)
					embed=discord.Embed(title="取得したRSS情報")
		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(RssCog(bot))

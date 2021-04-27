import asyncio
from distutils.util import strtobool

import discord


class EmbedManager:
	def __init__(self):
		pass

	async def generate(self, embed_title: str = None, embed_description: str = None, mode: str = None, embed_color: int = 0x8bc34a, embed_content: list = None):
		"""{'title': 'content', 'value': 'content', 'option': {'inline': 'False'}}"""
		if mode is not None:
			if mode == 'succeed':
				embed_color = 0x8bc34a
			elif mode == 'failed':
				embed_color = 0xd32f2f

		embed = discord.Embed(title=embed_title, description=embed_description, color=embed_color)
		for content in embed_content:
			title = content.get('title', 'タイトルが指定されていません')
			value = content.get('value', None)
			inline = content.get('option').get('inline')
			print(f"{content['title']}, {content['value']}")
			embed.add_field(name=title, value=value, inline=bool(strtobool(inline)))
		return embed

	async def send(self, ctx, embed, auto_delete: bool = False, sleep_time: int = None):
		msg = await ctx.send(embed=embed)
		if auto_delete is True:
			await asyncio.sleep(sleep_time)
			await msg.delete()
		return msg

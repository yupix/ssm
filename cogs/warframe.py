import discord
import numpy as np
import requests
from discord.ext import commands

from main import translator, db_commit, check_args, logger
from settings import session
from sql.models.WarframeFissure import WarframeFissuresMessage, WarframeFissuresId, WarframeFissuresDetail, WarframeFissuresChannel
from sql.models.blog import BlogsServer, BlogsCategory


def warframe_fissures_embed(mission_title, mission_type, appear_enemy, drop_relic, time_up_to_end):
	embed = discord.Embed(title=f'{mission_title}', description=f'ミッション内容: {mission_type}', color=0x859fff)
	embed.add_field(name=f"出現エネミー", value=f"{appear_enemy}", inline=True)
	embed.add_field(name=f"レリック", value=f"{drop_relic}", inline=True)
	embed.add_field(name=f"終了まで", value=f'{time_up_to_end}', inline=True)
	return embed


def mission_type_conversion(fissure_mission_type):
	conversion_list = {'Spy': '潜入', 'Capture': '確保', 'Survival': '耐久', 'Sabotage': '妨害', 'Defense': '防衛', 'Extermination': '殲滅', 'Rescue': '救出',
					   'Interception': '傍受', 'Mobile Defense': '機動防衛', 'Excavation': '発掘', 'Disruption': '分裂', 'Hijack': 'ハイジャック'}
	for conversion in conversion_list.keys():
		if fissure_mission_type == conversion:
			return fissure_mission_type.replace(conversion, conversion_list[f'{conversion}'])


def mission_eta_conversion(fissure_eta):
	conversion_list = {'h': '時間', 'm': '分', 's': '秒'}
	for conversion in conversion_list.keys():
		fissure_eta = fissure_eta.replace(conversion, conversion_list[f'{conversion}'])
	return fissure_eta


def challenge_title_conversion(challenge_title):
	conversion_list = {'Loyalty': '忠誠心', 'Detonator': '爆弾魔', 'Sidearm': 'サイドアーム', 'Cache Hunter': '貯蔵庫ハンター', 'Jailer': '投獄者',
					   'Invader': '侵略者', 'Friendly Fire': '誤射', 'Flawless': 'パーフェクト', 'Elite Explorer': 'エリート探検者',
					   'Choose Wisely': '決断', 'Swordsman': '剣客', 'Hacker': 'ハッカー', 'Biohazard': 'バイオハザード',
					   'Eximus Eliminator': 'エクシマス駆逐者', 'Conservationist': '保護主義者', 'Rescuer': '救出者', 'Now Boarding': '搭乗時刻',
					   'Defense': '防衛', 'Nothing but Profit': '利益こそ正義', 'Eliminator': '駆逐者', 'Poisoner': '毒殺者', 'Patron': 'パトロン',
					   'Silent Eliminator': '静かな駆逐者', 'Trampoline': 'トランポリン', 'Sword Dance': '剣の舞', 'Earth Bounty Hunter': '地球のバウンティハンター',
					   'Unlock Relics': 'レリックの開放', 'Earth Fisher': '地球の釣り人', 'Eximus Executioner': 'エクシマス処刑人'
					   }

	for conversion in conversion_list.keys():
		challenge_title = challenge_title.replace(conversion, conversion_list[f'{conversion}'])
	return challenge_title


def fissure_tier_conversion(tier):
	conversion_list = {'1': 'Lith', '2': 'Meso', '3': 'Neo', '4': 'Axi', '5': 'Requiem'}
	for conversion in conversion_list.keys():
		if tier == conversion:
			fissure_tier = tier.replace(conversion, conversion_list[f'{conversion}'])
			break
	return fissure_tier


def challenge_desc_conversion(challenge_desc):
	conversion_list = {'Interact with your Kubrow or Kavat': 'クブロウかキャバットと触れ合う',
					   'Kill 150 Enemies with Blast Damage': '150体の敵を爆発ダメージで倒す',
					   'Complete a Mission with only a Secondary Weapon equipped': 'セカンダリ武器のみを装備しミッションをクリアする',
					   'Find all caches in 3 Sabotage missions': '3回の妨害ミッションですべての貯蔵庫を見つける',
					   'Complete 3 Capture missions': '確保ミッションを3回クリアする',
					   'Complete 9 Invasion missions of any type': '侵略ミッションを9回クリアする',
					   'While piloting a hijacked Crewship, destroy 3 enemy Fighters': 'ハイジャックしたクルーシップを操縦中に敵の戦闘機を3機倒す',
					   'Clear a Railjack Boarding Party without your Warframe taking damage': 'WARFRAMEがダメージを受けずにレールジャック搭乗部隊をクリアする',
					   'Complete 8 Railjack Missions': 'レールジャックミッションを8回クリアする',
					   'Kill or Convert a Kuva Lich': 'クバリッチを抹殺もしくは転向させる',
					   'Complete a Mission with only a Melee Weapon equipped': '近接武器のみを装備しミッションをクリアする',
					   'Hack 8 Consoles': 'コンソールを8個ハッキングする',
					   'Kill 150 Enemies with Gas Damage': '150体の敵をガスダメージで倒す',
					   'Kill 30 Eximus': '30体のエクシマスを倒す',
					   'Complete 6 different Perfect Animal Captures in Orb Vallis': 'オーブ峡谷で完璧な異なる動物保護を6回クリアする',
					   'Complete 3 Rescue missions': '救出ミッションを3回クリアする',
					   'Complete 3 different K-Drive races in Orb Vallis': 'オーブ峡谷で3つの異なるK-ドライブレースを完了する',
					   'Complete a Defense mission reaching at least Wave 20': '防衛ミッションを最低20ウェーブまで進めてクリアする',
					   'Kill The Exploiter Orb': 'エクスプロイターオーブを倒す',
					   'Complete 3 Exterminate missions': '掃滅ミッションを3回クリアする',
					   'Kill 150 Enemies with Toxin Damage': '150体の敵を毒ダメージで倒す',
					   'Donate to the Leverian': 'レベリアンに寄付する',
					   'Complete an Extermination mission with level 30 or higher enemies without being detected': 'アラームを起動せずにレベル30以上の敵のみが生産される掃滅ミッションをクリアする',
					   'Bullet Jump 150 times': '150回バレットジャンプする',
					   'Kill 150 Enemies with a Melee Weapon': '150台の敵を近接武器で倒す',
					   'Complete 5 different Bounties in the Plains of Eidolon': 'エイドロンの草原で異なる依頼ミッションを5回クリアする',
					   'Unlock 3 Relics': 'レリックを3個開放する',
					   'Catch 6 Rare Fish in the Plains of Eidolon': 'エイドロンの草原で6匹のレアな魚を捕まえる',
					   'Kill 100 Eximus': '100体のエクシマスを倒す'
					   }
	for conversion in conversion_list.keys():
		challenge_desc = challenge_desc.replace(conversion, conversion_list[f'{conversion}'])
	return challenge_desc


def get_warframe_fissures_api():
	url = 'https://api.warframestat.us/pc/fissures'
	r = requests.get(url)

	if 'json' in r.headers.get('content-type'):
		r = r.json()
	else:
		return None
	fissure_list = []
	for count, fissure in enumerate(r):
		fissure_node = fissure.get('node')
		fissure_mission_type = fissure.get('missionType')
		fissure_enemy = fissure.get('enemy')
		fissure_tier = fissure.get('tier')
		fissure_eta = fissure.get('eta')
		fissure_id = fissure.get('id')
		fissure_expired = fissure.get('expired')
		conversion_list = {'Lith': '1', 'Meso': '2', 'Neo': '3', 'Axi': '4', 'Requiem': '5'}
		for conversion in conversion_list.keys():
			if fissure_tier == conversion:
				fissure_tier = fissure_tier.replace(conversion, conversion_list[f'{conversion}'])
		tmp_list = [fissure_node, mission_type_conversion(fissure_mission_type), fissure_enemy, fissure_tier, mission_eta_conversion(fissure_eta), fissure_id, fissure_expired]
		fissure_list.append(tmp_list)
	return fissure_list


class BlocklistCog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.group()
	async def warframe(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('this command is sub option required')

	@warframe.command()
	async def news(self, ctx):
		url = "https://api.warframestat.us/pc"
		r = requests.get(url).json()
		embed = discord.Embed(color=0x859fff)
		for i in r['news']:
			news_content = (i.get('translations').get('ja'))  # newsの内容を取得
			news_link = (i.get('link'))
			if news_content is None:
				news_content = (i.get('translations').get('en'))
			embed.add_field(name=f"{news_content}", value=f"{news_link}", inline=True)
		await ctx.send(embed=embed)

	@warframe.command()
	async def event(self, ctx):
		await db_commit(BlogsServer(server_id=f'{ctx.guild.id}'))
		await db_commit(BlogsCategory(server_id=f'{ctx.guild.id}', category_id=f'{ctx.channel.category.id}'))

	@warframe.command()
	async def voidtrader(self, ctx):
		url = 'https://api.warframestat.us/pc/voidTrader'
		r = requests.get(url).json()
		trader_location = r['location']
		trader_character = r['character']
		credit_emoji = self.bot.get_emoji(799707332208361493)
		ducats_emoji = self.bot.get_emoji(799708934671564811)
		embed = discord.Embed(title=f'{trader_location}', description=f'{trader_character}', color=0x859fff)
		for trade in r['inventory']:
			embed.add_field(name=f"{trade['item']}", value=f"{ducats_emoji} {trade['ducats']}\n{credit_emoji} {trade['credits']}", inline=True)
		await ctx.send(embed=embed)

	@warframe.command()
	async def nightwave(self, ctx):
		url = 'https://api.warframestat.us/pc/nightwave'
		r = requests.get(url).json()
		embed = discord.Embed(color=0x859fff)
		for count, nightwave in enumerate(r['activeChallenges']):
			challenge_title = nightwave['title']
			challenge_desc = nightwave['desc']
			embed.add_field(name=f"{challenge_title_conversion(challenge_title)}", value=f"{challenge_desc_conversion(challenge_desc)}", inline=True)
		await ctx.send(embed=embed)

	@warframe.command()
	async def sortie(self, ctx):
		url = 'https://api.warframestat.us/pc/sortie'
		r = requests.get(url).json()
		for count, sortie_variant in enumerate(r['variants']):
			sortie_variant_node = sortie_variant['node']
			sortie_variant_mission_type = sortie_variant['missionType']
			sortie_variant_modifier = sortie_variant['modifier']
			sortie_mission_desc = sortie_variant['modifierDescription']
			embed = discord.Embed(title=f'{sortie_variant_node}', description=f'ミッション内容: {mission_type_conversion(sortie_variant_mission_type)}', color=0x859fff)
			embed.add_field(name=f"効果", value=f"{translator(sortie_variant_modifier)}", inline=True)
			embed.add_field(name=f"概要", value=f"{translator(sortie_mission_desc)}", inline=True)
			await ctx.send(embed=embed)

	@warframe.command()
	async def fissures(self, ctx):
		fissure_list = get_warframe_fissures_api()
		b = np.array(fissure_list)
		index = np.argsort(b[:, 3])
		b_sorted = b[index, :]
		for i in b_sorted:
			conversion_list = {'1': 'Lith', '2': 'Meso', '3': 'Neo', '4': 'Axi', '5': 'Requiem'}
			for conversion in conversion_list.keys():
				if i[3] == conversion:
					fissure_tier = i[3].replace(conversion, conversion_list[f'{conversion}'])
			embed = discord.Embed(title=f'{i[0]}', description=f'ミッション内容: {i[1]}', color=0x859fff)
			embed.add_field(name=f"出現エネミー", value=f"{i[2]}", inline=True)
			embed.add_field(name=f"レリック", value=f"{fissure_tier}", inline=True)
			embed.add_field(name=f"終了まで", value=f'{i[4]}', inline=True)
			embed_message = await ctx.send(embed=embed)
			search_warframe_fissures_detail = session.query(WarframeFissuresDetail).filter(WarframeFissuresDetail.api_id == f'{i[5]}').first()
			logger.debug(search_warframe_fissures_detail.id)
			logger.debug(embed_message.id)
			await db_commit(WarframeFissuresChannel(channel_id=embed_message.channel.id))
			await db_commit(WarframeFissuresMessage(detail_id=search_warframe_fissures_detail.id, message_id=embed_message.id, channel_id=embed_message.channel.id))


def setup(bot):
	bot.add_cog(BlocklistCog(bot))

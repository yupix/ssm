import discord

import discord
import numpy as np
import requests
from discord.ext import commands

from main import translator


def mission_type_conversion(fissure_mission_type):
    conversion_list = {'Spy': '潜入', 'Capture': '確保', 'Survival': '耐久', 'Sabotage': '妨害', 'Defense': '防衛', 'Extermination': '殲滅', 'Rescue': '救出',
                       'Interception': '傍受', 'Mobile Defense': '機動防衛', 'Excavation': '発掘', 'Disruption': '分裂', 'Hijack': 'ハイジャック'}
    for conversion in conversion_list.keys():
        print(f'{fissure_mission_type}, {conversion}')
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
                       'Choose Wisely': '決断', 'Swordsman': '剣客'}

    for conversion in conversion_list.keys():
        challenge_title = challenge_title.replace(conversion, conversion_list[f'{conversion}'])
    return challenge_title


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
                       'Complete a Mission with only a Melee Weapon equipped': '近接武器のみを装備しミッションをクリアする'
                       }
    for conversion in conversion_list.keys():
        challenge_desc = challenge_desc.replace(conversion, conversion_list[f'{conversion}'])
    return challenge_desc

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
        url = "https://api.warframestat.us/pc"
        r = requests.get(url).json()
        embed = discord.Embed(color=0x859fff)
        for events in r['events']:
            event_jobs = events.get('jobs')
            if event_jobs is not None:
                for event_job in event_jobs:
                    event_jobs_type = event_job.get('type')
                    event_jpbs_enemylevels = event_job.get('enemyLevels')
                    print(event_jpbs_enemylevels)

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
        url = 'https://api.warframestat.us/pc/fissures'
        r = requests.get(url).json()
        fissure_list = []
        for count, fissure in enumerate(r):
            fissure_node = fissure.get('node')
            fissure_mission_type = fissure.get('missionType')
            fissure_enemy = fissure.get('enemy')
            fissure_tier = fissure.get('tier')
            fissure_eta = fissure.get('eta')
            conversion_list = {'Lith': '1', 'Meso': '2', 'Neo': '3', 'Axi': '4', 'Requiem': '5'}
            for conversion in conversion_list.keys():
                if fissure_tier == conversion:
                    fissure_tier = fissure_tier.replace(conversion, conversion_list[f'{conversion}'])
            tmp_list = [fissure_node, mission_type_conversion(fissure_mission_type), fissure_enemy, fissure_tier, mission_eta_conversion(fissure_eta)]
            fissure_list.append(tmp_list)
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
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(BlocklistCog(bot))

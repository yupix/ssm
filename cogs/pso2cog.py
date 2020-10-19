import csv
import re
from urllib.parse import urljoin

import requests
from discord.ext import commands
import urllib.request
from bs4 import BeautifulSoup


class Pso2Cog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def emergency(self, ctx):
        BASEURL = 'http://pso2.jp/players/'
        ENCODE = 'utf-8'

        # ---------- scrape base URL site ----------
        htmldata = requests.get(BASEURL)
        htmldata.encoding = ENCODE
        soup = BeautifulSoup(htmldata.content, 'lxml')
        href_list = list(set(soup.find_all('a', href='boost/')))
        # ---------- get boost quest URL ----------
        boost_url = urljoin(BASEURL, href_list[0].get('href'))
        # ---------- scrape boost quest timetable ----------
        boostdata = requests.get(boost_url)
        boostdata.encoding = ENCODE
        boostsoup = BeautifulSoup(boostdata.content, 'lxml')

        WEEKDAYS = {
            0: 'monday',
            1: 'tuesday',
            2: 'wednesday',
            3: 'thursday',
            4: 'friday',
            5: 'saturday',
            6: 'sunday'
        }

        with open("ebooks.csv", "w", encoding='utf-8') as file:
            writer = csv.writer(file)
            for WEEKDAYS_DATA in WEEKDAYS.values():
                today_quests = list(set(boostsoup.find_all('td', class_='day-{0}'.format(WEEKDAYS_DATA))))
                quest_info = [str(content.div) for content in today_quests]
                for quest in quest_info:
                    info = re.split('[<,>]', quest)
            #SLACK_INFO = []
            #SLACK_INFO += '{0}{1} {2} {3}\n'.format(info[18].replace('～', '-'), info[22], info[10], info[4])
                #print(SLACK_INFO)
                #csvRow.append(info.get_text())
                #writer.writerow(csvRow)


def setup(bot):
    bot.add_cog(Pso2Cog(bot))

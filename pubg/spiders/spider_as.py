'''
AS info spider
'''
# -*- coding: utf-8 -*-
import re
import json
import argparse
import time

import scrapy
from scrapy.selector import Selector
import leveldb
from pubg_api.api import get_key
try:
    _we_chat = __import__('itchat')
except:
    print('Load wechat library failed, run withou notification')
    has_we_chat = False
else:
    globals()['itchat'] = _we_chat
    has_we_chat = False

# print(has_we_chat)
if has_we_chat:
    itchat.auto_login(hotReload=True)
    itchat.send(u'Start Notifying', 'filehelper')

parser = argparse.ArgumentParser(description='ASSpider')
parser.add_argument('N',type=int,nargs='?',help='number of pages',default=30)
parser.add_argument('S',type=int,nargs='?',help='start index of pages',default=1)
parser.add_argument('L',type=int,nargs='?',help='set 1 to lilst only',default=0)
args = parser.parse_args()
print( args )

import os
curr_dir_path = os.path.dirname(os.path.realpath(__file__))

class Spider_AS(scrapy.Spider):
    print('Spider As Called')
    name = "spider_as"
    allowed_domains = ["pubgtracker.com"]

    start_urls = (
        'https://pubgtracker.com/leaderboards/pc/Rating?page=%d&mode=3&region=3'%(args.S),
    )
    base = 'https://pubgtracker.com/leaderboards/pc/Rating?'
    p = re.compile(r'.*page=([0-9]+)&.*')
    user_db = None # leveldb.LevelDB('./user_db')
    pubg_api_key = get_key(curr_dir_path+'/../../.PRIVATE')

    file_ids = open('user_ids.txt', 'w')

    def parse(self, response):
        if self.user_db == None:
            self.user_db = leveldb.LevelDB('./user_db')
        match = self.p.match(response.url)
        current_page = int(match.group(1))
        print('current_page =', current_page)
        body = response.body
        els = Selector(text=body).xpath("//table[@class='card-table-material']/tbody")[0]

        for tr in els.xpath('tr'):
            tds = tr.xpath('td')
            if(len(tds) < 2):
                continue
            rank = tds[0].xpath('text()').extract()[0].strip()
            name_node = tds[1].xpath("a[@data-tooltip='notooltip']")
            href = name_node.xpath('@href').extract()[0].strip()
            id = name_node.xpath('text()').extract()[0].strip()
            rating = tds[2].xpath("div[@class='pull-right']/text()").extract()[0].strip()
            n_game = tds[3].xpath('text()').extract()[0].strip()
            print(rank, id, href, rating, n_game)
            self.file_ids.write('%d %s %f %d\n', rank, id, rating, n_game)
            if args.L == 1:
                continue
            if len(self.pubg_api_key) == 0: # no key
                yield scrapy.Request(url = 'https://pubgtracker.com/profile/pc/%s/squad?region=as'%(id),
                                    callback=self.parse_user)
            else:
                yield scrapy.Request(url = 'https://pubgtracker.com/api/profile/pc/%s'%(id),
                                     headers= { 'TRN-Api-Key': self.pubg_api_key },
                                     callback=self.parse_user_api)
        next_page = Selector(text=body).xpath("//a[@class='next next-page']")
        print(next_page.extract())
        if len(next_page.xpath('@disabled')) == 0:
            # do next page
            url_patern = 'https://pubgtracker.com/leaderboards/pc/Rating?page=%d&mode=3&region=3'
            next_url = url_patern % (current_page + 1)
            print('next_page =', next_url )
            if has_we_chat:
                if current_page % 5 == 0:
                    itchat.send(u'Working on '+ next_url, 'filehelper')
            if current_page < args.N :
                if current_page == -1:
                    yield scrapy.Request(url=next_url, meta={"dont_cache": True}, callback=self.parse)
                else:
                    yield scrapy.Request(url=next_url, callback=self.parse )
        return

    user_cnt = 0
    last_time = time.time()

    def save_user(self, user_object, raw_object):
        try:
            user = self.user_db.Get(user_object['PlayerName'])
            print(user_object['PlayerName'], 'existed!')
        except KeyError:
            self.user_db.Put(user_object['PlayerName'], bytearray(raw_object, 'utf8'))

    def parse_user_api(self, response):
        body = response.body
        player_info = json.loads(body)
        try:
            print(player_info['PlayerName'])
            self.save_user(player_info, body)
        except KeyError:
            pass
        self.user_cnt += 1
        if( self.user_cnt % 200 == 0) and has_we_chat:
            now_time = time.time()
            elapsed_time = now_time - self.last_time
            self.last_time = now_time
            itchat.send('200 Users in %d seconds'%elapsed_time)

    def parse_user(self, response):
        # https://pubgtracker.com/profile/pc/Maesaengi/squad?region=as
        body = response.body
        els = Selector(text=body).xpath("//script[@type='text/javascript']")
        for e in els:
            content = e.xpath('text()').extract_first()
            if content.find('playerData') > -1:
                # now info is in this dict
                player_info = json.loads(content[17:-1])
                self.save_user(player_info, content[17:-1])

    def __del__(self):
        self.user_db.Close()
        self.file_ids.close()
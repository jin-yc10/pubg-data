'''
AS info spider
'''
# -*- coding: utf-8 -*-
import re
import json
import argparse

import scrapy
from scrapy.selector import Selector
import leveldb

try:
    _we_chat = __import__(wechat)
except:
    print('Load wechat library failed, run withou notification')    

parser = argparse.ArgumentParser(description='EUSpider')
parser.add_argument('N',type=int,nargs='?',help='number of pages',default=30)
parser.add_argument('S',type=int,nargs='?',help='start index of pages',default=1)
parser.add_argument('L',type=int,nargs='?',help='set 1 to lilst only',default=0)
args = parser.parse_args()
print( args )

class EUSpider(scrapy.Spider):
    name = "eu"
    allowed_domains = ["pubgtracker.com"]

    start_urls = (
        'https://pubgtracker.com/leaderboards/pc/Rating?page=%d&mode=3&region=3'%(args.S),
    )
    base = 'https://pubgtracker.com/leaderboards/pc/Rating?'
    p = re.compile(r'.*page=([0-9]+)&.*')
    user_db = leveldb.LevelDB('./user_db_win')

    def parse(self, response):
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
            if args.L == 1:
                continue
            yield scrapy.Request(url = 'https://pubgtracker.com/profile/pc/%s/squad?region=as'%(id),
                                  callback=self.parse_user)
        next_page = Selector(text=body).xpath("//a[@class='next next-page']")
        print(next_page.extract())
        if len(next_page.xpath('@disabled')) == 0:
            # do next page
            url_patern = 'https://pubgtracker.com/leaderboards/pc/Rating?page=%d&mode=3&region=3'
            next_url = url_patern % (current_page + 1)
            print('next_page =', next_url )
            if current_page < args.N :
                if current_page == -1:
                    yield scrapy.Request(url=next_url, meta={"dont_cache": True}, callback=self.parse)
                else:
                    yield scrapy.Request(url=next_url, callback=self.parse )
        return

    def parse_user(self, response):
        # https://pubgtracker.com/profile/pc/Maesaengi/squad?region=as
        body = response.body
        els = Selector(text=body).xpath("//script[@type='text/javascript']")
        for e in els:
            content = e.xpath('text()').extract_first()
            if content.find('playerData') > -1:
                # now info is in this dict
                player_info = json.loads(content[17:-1])
                try:
                    user = self.user_db.Get(player_info['AccountId'])
                    print(player_info['AccountId'], 'existed!')
                except KeyError:
                    self.user_db.Put(player_info['AccountId'], bytearray(content[17:-1], 'utf8'))

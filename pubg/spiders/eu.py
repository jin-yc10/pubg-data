# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
import wget
# http://dlsys.cs.washington.edu/schedule
import re
class EUSpider(scrapy.Spider):
    name = "eu"
    # allowed_domains = ["stanford.edu"]
    allowed_domains = ["pubgtracker.com"]

    start_urls = (
        'https://pubgtracker.com/leaderboards/pc/Rating?page=1&mode=3&region=3',
    )
    base = 'https://pubgtracker.com/leaderboards/pc/Rating?'
    p = re.compile(r'.*page=([0-9]+)&.*')

    def parse(self, response):
        match = self.p.match(response.url)
        current_page = int(match.group(1))
        print('current_page =',current_page)
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
        next_page = Selector(text=body).xpath("//a[@class='next next-page']")
        print(next_page.extract())
        if len(next_page.xpath('@disabled')) == 0:
            # do next page
            url_patern = 'https://pubgtracker.com/leaderboards/pc/Rating?page=%d&mode=3&region=3'
            next_url = url_patern % (current_page + 1)
            print('next_page =', next_url )
            if( current_page < 5 ):
                return scrapy.Request(url=next_url, callback=self.parse )
            else:
                return

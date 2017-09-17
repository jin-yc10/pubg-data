# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
import wget
# http://dlsys.cs.washington.edu/schedule
class PdfExtractSpider(scrapy.Spider):
    name = "pdf_extract"
    # allowed_domains = ["stanford.edu"]
    allowed_domains = ["washington.edu"]

    start_urls = (
        # 'http://cs224d.stanford.edu/syllabus.html',
        # 'http://web.stanford.edu/class/cs20si/syllabus.html',
        'http://dlsys.cs.washington.edu/schedule',
    )
    base = 'http://dlsys.cs.washington.edu'
# openssl s_client -connect "web.stanford.edu:443" -servername "web.stanford.edu"
    def parse(self, response):
        body = response.body
        els = Selector(text=body).xpath('//a')
        for e in els:
            text = e.xpath('text()').extract()
            href = e.xpath('@href').extract()[0]
            if href.find('pubg') > -1:
                url = ''
                if href.find('http') > -1:
                    print "direct", href
                    url = href
                else:
                    print "base+", self.base + href
                    url = self.base + href
                n = wget.download(url, bar=wget.bar_adaptive)
                print n, ' downloaded!'
            # print text
            # if text[0] == u'.pdf':
            #     url = self.base + e.xpath('@href').extract()[0]
            #     print url
            #     n = wget.download(url, bar=wget.bar_adaptive)
            #     print n, ' downloaded!'

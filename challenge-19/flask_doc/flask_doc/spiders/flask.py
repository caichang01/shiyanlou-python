# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from flask_doc.items import PageItem


class FlaskSpider(scrapy.spiders.CrawlSpider):
    name = 'flask'
    allowed_domains = ['flask.pocoo.org']
    start_urls = ['http://flask.pocoo.org/docs/0.12/']

    rules = (
        Rule(LinkExtractor(allow='http://flask.pocoo.org/docs/0.12/.*'),
             callback='page_parse', follow=True),
    )

    def page_parse(self, response):
        item = PageItem()

        item['url'] = response.url
        item['text'] = ' '.join(response.xpath('//text()').extract())
        yield item

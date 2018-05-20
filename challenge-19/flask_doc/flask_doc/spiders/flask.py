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
             callback='parse', follow=True),
    )

    def parse(self, response):
        item = PageItem()

        item['url'] = response.url

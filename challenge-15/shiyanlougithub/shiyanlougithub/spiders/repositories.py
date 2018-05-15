# -*- coding: utf-8 -*-
import scrapy


class RepositoriesSpider(scrapy.Spider):
    name = 'repositories'
    start_urls = ['https://github.com/shiyanlou?tab=repositories/']

    def parse(self, response):
        pass

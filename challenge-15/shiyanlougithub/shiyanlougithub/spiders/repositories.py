# -*- coding: utf-8 -*-
import scrapy
from shiyanlougithub.items import ShiyanlougithubItem


class RepositoriesSpider(scrapy.Spider):
    name = 'repositories'

    @property
    def start_urls(self):
        url_templ = 'https://github.com/shiyanlou?page={}&tab=repositories'
        return (url_templ.format(i) for i in range(1, 5))

    def parse(self, response):
        for repository in response.css('div#user-repositories-list > ul > li'):
            yield ShiyanlougithubItem({
                'name': repository.css('div.d-inline-block.mb-1 h3 a::text')
                .re_first(r'[^\S]*(.+)[^\S]*'),
                'update_time': repository.css('div.f6.text-gray.mt-2 \
                relative-time::attr(datetime)').extract_first()
            })

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
            item = ShiyanlougithubItem()

            item['name'] = repository.css('div.d-inline-block.mb-1 \
            h3 a::text').re_first(r'[^\S]*(.+)[^\S]*')

            item['update_time'] = repository.css('div.f6.text-gray.mt-2 \
            relative-time::attr(datetime)').extract_first()

            repository_url = response.urljoin(repository.xpath('.//a/@href\
            ').extract_first())
            request = scrapy.Request(repository_url, callback=self.parse_repo)
            request.meta['item'] = item

            yield request

    def parse_repo(self, response):
        item = response.meta['item']

        item['commits'] = response.xpath('//ul[@class="numbers-summary"]/li[1]\
        /a/span/text()').re_first(r'[^\d]*(.+)[^\d]*')
        item['branches'] = response.xpath('//ul[@class="numbers-summary"]/li[2]\
        /a/span/text()').re_first(r'[^\d]*(.+)[^\d]*')
        item['releases'] = response.xpath('//ul[@class="numbers-summary"]/li[3]\
        /a/span/text()').re_first(r'[^\d]*(.+)[^\d]*')

        yield item

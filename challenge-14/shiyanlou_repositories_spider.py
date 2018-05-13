import scrapy


class ShiyanlouRepositoriesSpider(scrapy.Spider):
    name = 'shiyanlou-repositories'

    @property
    def start_urls(self):
        url_templ = 'https://github.com/shiyanlou?page={}&tab=repositories'
        return (url_templ.format(i) for i in range(1, 5))
    
    def parse(self, response):
        for repository in response.css('div#user-repositories-list'):
            yield{
                'name': repository.css('div#user-repositories-list > ul > li:nth-child(1) > div.d-inline-block.mb-1 h3::text').extract_first()
            }
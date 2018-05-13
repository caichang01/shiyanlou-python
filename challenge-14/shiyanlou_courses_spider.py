import scrapy


class ShiyanlouCoursesSpider(scrapy.Spider):
    # 爬虫标识符，name用于标识每个爬虫，不能相同
    name = 'shiyanlou-courses'

    def start_requests(self):
        # 课程页面url模板
        url_templ = 'http://www.shiyanlou.com/courses/?category=all&course_type=all&fee=all&tag=all&page={}'
        # 所有要爬取的页面
        urls = (url_templ.format(i) for i in range(1, 23))
        # 返回一个生成器，生成Request对象，生成器是可迭代对象
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # 遍历每个课程的 div.course-body
        for course in response.css('div.course-body'):
            yield{
                  'name': course.css('div.course-name::text').extract_first(),
                  'description': course.css('div.course-desc::text').extract_first(),
                  'type': course.css('div.course-footer span.pull-right::text').extract_first(default='Free'),
                  'students': course.xpath('.//span[contains(@class, "pull-left")]/text()[2]').re_first('[^\d]*(\d+)[^\d]*')
            }
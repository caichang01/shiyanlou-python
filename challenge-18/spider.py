# 引入 json 包用来序列化
import json

# 引入 selenium 相关内容
from selenium import webdriver
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

# 存储爬取的结果
results = []


# 使用 xpath 解析评论数据
def parse(response):
    for comment in response.css('div.comment-list-item'):
        # 使用 xpath 提取 HTML 里的评论者昵称 name 和评论内容 content
        # 并存入字典 result，然后将 result 添加到列表 results 中
        result = dict((
            ('name', comment.xpath('.//a[@class="username"]/text()')
             .extract_first().strip()),
            ('content', comment.xpath('.//div[contains(@class, \
            "comment-item-content")]/p/text()').extract_first())
        ))
        results.append(result)


# 判断是否有下一页
def has_next_page(response):
    # 使用 xpath 提取数据来判断是否存在下一页
    # 返回 True 或者 False
    class_list = response.xpath('//li[contains(@class, "next-page")]\
    /@class').extract_first()
    # 出现bug的原因是，未加extract_first方法调用，这样返回的是对象，其后的判断永远是真值

    if 'disabled' in class_list:
        return False
    else:
        return True


# 进入到下一页
def goto_next_page(driver):
    # 使用 driver.find_element_by_xpath 获得下一页的按钮
    # 然后模拟按钮的 click() 操作进入到下一页
    next_page_btn = driver.find_element_by_xpath('//li[@class="next-page"]')
    next_page_btn.click()


# 等待页面加载完成
def wait_page_return(driver, page):
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.XPATH, '//ul[@class="pagination"]/li[@class="active"]'),
            str(page)
        )
    )


# 主函数
def spider():
    # 创建 Chrome 的 webdriver
    driver = webdriver.Chrome(chrome_options=chrome_options)
    # 获取第一个页面
    url = 'https://www.shiyanlou.com/courses/427'
    driver.get(url)
    page = 1
    while True:
        # 加载评论的第一页
        wait_page_return(driver, page)
        # 获取页面源码
        html = driver.page_source
        # 构建 HtmlResponse 对象
        response = HtmlResponse(url=url, body=html.encode('utf8'))
        # 解析 HtmlResponse 对象获取评论数据
        parse(response)
        # 如果是最后一页则停止爬取
        if not has_next_page(response):
            break
        # 进入到下一页
        page += 1
        goto_next_page(driver)
    # 将 results 使用 json 序列化后写入文件
    with open('./comments.json', 'w') as f:
        f.write(json.dumps(results))
    driver.close()


if __name__ == '__main__':
    spider()

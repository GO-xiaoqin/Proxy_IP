import time

import scrapy
from scrapy.http import Request
from ProxyIP_Spider.items import ProxyipSpiderItem
from twisted.internet.error import TimeoutError, TCPTimedOutError, ConnectionRefusedError
from scrapy.spidermiddlewares.httperror import HttpError

import re
import random

"""
快代理
"""


class ProxySpider(scrapy.Spider):
    name = 'k_proxy'

    def start_requests(self):
        url = "https://www.kuaidaili.com/free/"
        yield Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        proxy_item = dict()
        proxy_list = response.xpath('//*[contains(@class,"table-bordered")]//tr')
        for i in proxy_list:
            proxy_ip = i.xpath('.//*[@data-title="IP"]/text()').get()
            proxy_port = i.xpath('.//*[@data-title="PORT"]/text()').get()
            proxy_anonymity = i.xpath('.//*[@data-title="匿名度"]/text()').get()
            proxy_type = i.xpath('.//*[@data-title="类型"]/text()').get()
            proxy_response_speed = i.xpath('.//*[@data-title="响应速度"]/text()').get()
            proxy_verification_time = i.xpath('.//*[@data-title="最后验证时间"]/text()').re(r'\d+-\d+-\d+')
            # 进行过滤筛选
            if not all([
                proxy_ip, proxy_port, proxy_anonymity, proxy_type, proxy_response_speed, proxy_verification_time
            ]) or "匿" not in proxy_anonymity:
                continue
            proxy_item['proxy_ip'] = proxy_ip
            proxy_item['proxy_port'] = proxy_port
            proxy_item['proxy_anonymity'] = proxy_anonymity
            proxy_item['proxy_type'] = proxy_type
            proxy_item['proxy_response_speed'] = proxy_response_speed
            proxy_item['proxy_verification_time'] = proxy_verification_time

            proxy_item['proxy'] = "http://{}:{}".format(proxy_ip, proxy_port)
            if str(proxy_item['proxy_type']).lower() == "https":
                proxy_item['proxy'] = "https://{}:{}".format(proxy_ip, proxy_port)

            p = re.compile(r'(.*?)秒')
            try:
                timeout = p.findall(proxy_response_speed)[0]
            except IndexError:
                self.logger.error("网站有变动，请查看!!!")
                break
            try:
                proxy_item['download_timeout'] = int(timeout) + 3
            except ValueError:
                proxy_item['download_timeout'] = int(float(timeout)) + 3
            except Exception as e:
                self.logger.error("error as {}".format(e))
                break

            self.logger.info("Ready to test {}".format(proxy_item['proxy']))
            r_url = ["http://httpbin.org/ip",
                     "http://ip-api.com/json/?lang=zh-CN"]
            yield Request(
                url=random.choice(r_url), dont_filter=True, callback=self.verify,
                meta=proxy_item, errback=self.errback_f
            )

        # next page
        today = time.strptime(time.strftime("%Y%m%d", time.localtime()), "%Y%m%d")
        if proxy_item and time.strptime(proxy_item['proxy_verification_time'][0], "%Y-%m-%d") == today:
            the_page = response.xpath('//*[@id="listnav"]//li/a[@class="active"]/text()').get()
            next_page = "https://www.kuaidaili.com/free/inha/{}/".format(int(the_page) + 1)
            yield Request(url=next_page, dont_filter=True, callback=self.parse)
        else:
            return

    def errback_f(self, failure):
        # 校验失败的处理
        meta = failure.request.meta
        proxy_item = ProxyipSpiderItem()
        proxy_item['proxy'] = meta['proxy']
        proxy_item['proxy_ip'] = meta['proxy_ip']
        proxy_item['proxy_port'] = meta['proxy_port']
        proxy_item['proxy_anonymity'] = meta['proxy_anonymity']
        proxy_item['proxy_type'] = meta['proxy_type']
        proxy_item['proxy_response_speed'] = meta['download_timeout']
        proxy_item['status'] = False
        yield proxy_item

    def verify(self, response):
        # 　校验成功处理
        meta = response.meta
        proxy_item = ProxyipSpiderItem()
        proxy_item['proxy'] = meta['proxy']
        proxy_item['proxy_ip'] = meta['proxy_ip']
        proxy_item['proxy_port'] = meta['proxy_port']
        proxy_item['proxy_anonymity'] = meta['proxy_anonymity']
        proxy_item['proxy_type'] = meta['proxy_type']
        proxy_item['proxy_response_speed'] = meta['download_timeout']
        proxy_item['status'] = True
        yield proxy_item

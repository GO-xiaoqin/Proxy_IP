from urllib import parse

import scrapy

from scrapy.http import Request
from ProxyIP_Spider.items import ProxyipSpiderItem

import re
import random

"""
无忧代理
"""


class ProxySpider(scrapy.Spider):
    name = 'wy_proxy'

    def start_requests(self):
        url = "http://www.data5u.com/"
        yield Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        proxy_item = dict()
        proxy_list = response.xpath('//*[@class="wlist"]//ul[@class="l2"]')
        for i in proxy_list:
            proxy_ip = i.xpath('./span[1]//text()').get()
            proxy_port = i.xpath('./span[2]//text()').get()
            proxy_anonymity = i.xpath('./span[3]//text()').get()
            proxy_type = i.xpath('./span[4]//text()').get()
            proxy_response_speed = i.xpath('./span[8]//text()').get()
            proxy_verification_time = i.xpath('./span[last()]//text()').get()
            # 进行过滤筛选
            if not all([
                proxy_ip, proxy_port, proxy_anonymity, proxy_type, proxy_response_speed, proxy_verification_time
            ]) or "匿" not in proxy_anonymity:
                continue
            proxy_item['proxy_ip'] = proxy_ip
            proxy_item['proxy_port'] = proxy_port
            proxy_item['proxy_anonymity'] = proxy_anonymity
            proxy_item['proxy_type'] = proxy_type
            proxy_item['proxy_request_type'] = "GET"
            proxy_item['proxy_response_speed'] = proxy_response_speed
            proxy_item['proxy_verification_time'] = proxy_verification_time

            proxy_item['proxy'] = "http://{}:{}".format(proxy_item['proxy_ip'], proxy_item['proxy_port'])
            if str(proxy_item['proxy_type']).lower() == "https":
                proxy_item['proxy'] = "https://{}:{}".format(proxy_item['proxy_ip'], proxy_item['proxy_port'])

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

            # self.logger.info(proxy_item)
            self.logger.info("Ready to test {}".format(proxy_item['proxy']))
            r_url = ["http://httpbin.org/ip",
                     "http://ip-api.com/json/?lang=zh-CN"]
            yield Request(
                url=random.choice(r_url), dont_filter=True, callback=self.verify,
                meta=proxy_item, errback=self.errback_f
            )

    def errback_f(self, failure):
        # 校验失败的处理
        meta = failure.request.meta
        proxy_item = ProxyipSpiderItem()
        proxy_item['proxy'] = meta['proxy']
        proxy_item['proxy_ip'] = meta['proxy_ip']
        proxy_item['proxy_port'] = meta['proxy_port']
        proxy_item['proxy_anonymity'] = meta['proxy_anonymity']
        proxy_item['proxy_type'] = meta['proxy_type']
        proxy_item['proxy_request_type'] = meta['proxy_request_type']
        proxy_item['proxy_response_speed'] = meta['download_timeout']
        proxy_item['status'] = False
        yield proxy_item

    def verify(self, response):
        # 校验成功处理
        meta = response.meta
        proxy_item = ProxyipSpiderItem()
        proxy_item['proxy'] = meta['proxy']
        proxy_item['proxy_ip'] = meta['proxy_ip']
        proxy_item['proxy_port'] = meta['proxy_port']
        proxy_item['proxy_anonymity'] = meta['proxy_anonymity']
        proxy_item['proxy_type'] = meta['proxy_type']
        proxy_item['proxy_request_type'] = meta['proxy_request_type']
        proxy_item['proxy_response_speed'] = meta['download_timeout']
        proxy_item['status'] = True
        yield proxy_item

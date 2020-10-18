import random
import re

import scrapy
from scrapy.http import Request

from ProxyIP_Spider.items import ProxyipSpiderItem

"""
智连HTTP代理
"""


class ProxySpider(scrapy.Spider):
    name = 'zl_proxy'

    def start_requests(self):
        url = "http://http.zhiliandaili.cn/"
        yield Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        proxy_item = dict()
        proxy_list = response.xpath('//*[@class="lineTable w1200"]//tr')
        for i in proxy_list:
            proxy_ip = i.xpath('.//th[1]//text()').get()
            proxy_port = i.xpath('.//th[2]//text()').get()
            proxy_anonymity = i.xpath('.//th[last()]//text()').get()
            # 进行过滤筛选
            if not all([proxy_ip, proxy_port, proxy_anonymity]) or "匿" not in proxy_anonymity \
                    or not re.findall(r"\d+\.\d+\.\d+\.\d+", proxy_ip) or not re.findall(r"\d+", proxy_port):
                continue
            proxy_item['proxy_ip'] = str(proxy_ip).strip()
            proxy_item['proxy_port'] = str(proxy_port).strip()
            proxy_item['proxy_anonymity'] = "匿名"
            proxy_item['proxy_type'] = "HTTP"
            proxy_item['proxy_request_type'] = "GET"
            # 没有响应时间，直接设置
            proxy_item['download_timeout'] = 5

            proxy_item['proxy'] = "http://{}:{}".format(proxy_item['proxy_ip'], proxy_item['proxy_port'])
            if str(proxy_item['proxy_type']).lower() == "https":
                proxy_item['proxy'] = "https://{}:{}".format(proxy_item['proxy_ip'], proxy_item['proxy_port'])

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

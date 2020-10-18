from urllib import parse

import scrapy

from scrapy.http import Request
from scrapy_splash import SplashRequest

from ProxyIP_Spider.items import ProxyipSpiderItem

import re
import random

"""
站大爷代理
"""


class ProxySpider(scrapy.Spider):
    name = 'zdy_proxy'

    def start_requests(self):
        url = "https://www.zdaye.com/FreeIPList.html"
        yield SplashRequest(url=url, callback=self.parse, args={"wait": 5})

    def parse(self, response):
        proxy_item = dict()
        proxy_list = response.xpath('//*[@id="ipc"]//tr')
        for i in proxy_list:
            proxy_ip = i.xpath('.//td[1]//text()').get()
            proxy_port = i.xpath('.//td[3]/img/@src').get()     # TODO 端口为图片网址要进行识别
            proxy_anonymity = i.xpath('.//td[4]//text()').get()     # 未知，透明，匿名
            proxy_type = i.xpath('.//td[7]//node()').get()
            proxy_request_type = i.xpath('.//td[8]//node()').get()
            proxy_response_speed = i.xpath('.//td[9]//text()').get()
            # 进行过滤筛选
            if not all([
                proxy_ip, proxy_port, proxy_anonymity, proxy_response_speed
            ]) or "透明" in proxy_anonymity:
                continue
            proxy_item['proxy_ip'] = proxy_ip
            proxy_item['proxy_port'] = proxy_port
            proxy_item['proxy_anonymity'] = proxy_anonymity
            proxy_item['proxy_type'] = "HTTP" if not proxy_type else "HTTPS"
            proxy_item['proxy_request_type'] = "GET" if not proxy_request_type else "GET/POST"
            proxy_item['proxy_response_speed'] = proxy_response_speed

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

            self.logger.info(proxy_item)
            # self.logger.info("Ready to test {}".format(proxy_item['proxy']))
            # r_url = ["http://httpbin.org/ip",
            #          "http://ip-api.com/json/?lang=zh-CN"]
            # yield Request(
            #     url=random.choice(r_url), dont_filter=True, callback=self.verify,
            #     meta=proxy_item, errback=self.errback_f
            # )

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

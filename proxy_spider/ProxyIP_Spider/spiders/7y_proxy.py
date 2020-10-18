import time
from urllib import parse

import scrapy

from scrapy.http import Request
from ProxyIP_Spider.items import ProxyipSpiderItem

import re
import random

"""
齐云代理
"""


class ProxySpider(scrapy.Spider):
    name = '7y_proxy'

    def start_requests(self):
        url = "https://www.7yip.cn/free/"
        yield Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        proxy_item = dict()
        proxy_list = response.xpath('//*[contains(@class,"table-bordered")]//tr')
        for i in proxy_list:
            proxy_ip = i.xpath('.//td[@data-title="IP"]/text()').get()
            proxy_port = i.xpath('.//td[@data-title="PORT"]/text()').get()
            proxy_anonymity = i.xpath('.//td[@data-title="匿名度"]/text()').get()
            proxy_type = i.xpath('.//td[@data-title="类型"]/text()').get()
            proxy_response_speed = i.xpath('.//td[@data-title="响应速度"]/text()').get()
            proxy_verification_time = i.xpath('.//td[last()]/text()').get()
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

        # next page
        if proxy_item:
            today = time.strptime(time.strftime("%Y%m%d", time.localtime()), "%Y%m%d")
            ip_date = time.strptime(
                time.strftime(
                    "%Y%m%d", time.strptime(proxy_item['proxy_verification_time'], "%Y-%m-%d %H:%M:%S")
                ), "%Y%m%d"
            )
            if ip_date == today:
                next_page = response.xpath('//*[@class="pagination"]/li[last()]/a/@href').get()
                next_page_url = parse.urljoin(response.request.url, next_page)
                yield Request(url=next_page_url, dont_filter=True, callback=self.parse)
            else:
                return
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

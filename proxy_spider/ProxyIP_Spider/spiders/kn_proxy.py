import re
import random
import scrapy

from scrapy.http import Request
from ProxyIP_Spider.items import ProxyipSpiderItem

"""
快鸟代理
"""


class ProxySpider(scrapy.Spider):
    name = 'kn_proxy'

    def start_requests(self):
        url = "http://www.kuainiaoip.com/support/c/free-proxy-ip.html"
        yield Request(url, callback=self.parse_, dont_filter=True)

    def parse_(self, response):
        detail_url = response.xpath(
            '//*[@class="list-unstyled"]/li[1]//*[contains(@class,"media-body")]/a[1]/@href'
        ).get()
        yield Request(detail_url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        proxy_item = dict()
        proxy_detail = response.xpath('//*[@class="article-text"]//text()').extract()
        p = re.compile(r'\d+\.\d+\.\d+\.\d+:\d+')
        proxy_list = p.findall('\n'.join(proxy_detail))

        for i in proxy_list:
            proxy_item['proxy_ip'] = str(i).split(":")[0]
            proxy_item['proxy_port'] = str(i).split(":")[1]
            proxy_item['proxy_anonymity'] = "匿名"
            proxy_item['proxy_type'] = "HTTP"
            proxy_item['proxy_request_type'] = "GET"
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

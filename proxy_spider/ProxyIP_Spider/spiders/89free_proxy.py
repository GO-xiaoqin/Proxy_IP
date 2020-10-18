import time
import random
import scrapy
from urllib import parse
from scrapy.http import Request

from ProxyIP_Spider.items import ProxyipSpiderItem

"""
89免费代理
"""


class ProxySpider(scrapy.Spider):
    name = '89free_proxy'

    def start_requests(self):
        url = "https://www.89ip.cn/"
        yield Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        proxy_item = dict()
        proxy_list = response.xpath('//*[@class="layui-form"]/table//tr')
        for i in proxy_list:
            proxy_ip = i.xpath('.//td[1]//text()').get()
            proxy_port = i.xpath('.//td[2]//text()').get()
            proxy_verification_time = i.xpath('.//td[last()]//text()').get()
            # 进行过滤筛选
            if not all([proxy_ip, proxy_port, proxy_verification_time]):
                continue
            proxy_item['proxy_ip'] = str(proxy_ip).strip()
            proxy_item['proxy_port'] = str(proxy_port).strip()
            proxy_item['proxy_anonymity'] = "匿名"
            proxy_item['proxy_type'] = "HTTP"
            proxy_item['proxy_request_type'] = "GET"
            proxy_item['proxy_verification_time'] = str(proxy_verification_time).strip()
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

        # next page
        if proxy_item:
            today = time.strptime(time.strftime("%Y%m%d", time.localtime()), "%Y%m%d")
            ip_date = time.strptime(
                time.strftime(
                    "%Y%m%d", time.strptime(proxy_item['proxy_verification_time'], "%Y/%m/%d %H:%M:%S")
                ), "%Y%m%d"
            )
            if ip_date == today:
                next_page = response.xpath('//*[@class="fly-panel"]/div//a[@class="layui-laypage-next"]/@href').get()
                next_page_url = parse.urljoin(response.request.url, next_page)
                time.sleep(1.8)
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

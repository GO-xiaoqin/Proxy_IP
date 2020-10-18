import requests
import scrapy
import OpenSSL
from twisted.internet.error import TimeoutError
from scrapy import Request
from scrapy_splash import SplashRequest


class TestSpider(scrapy.Spider):
    name = 'test'

    def start_requests(self):
        url = "https://www.zdaye.com/FreeIPList.html"
        # meta = {
        #     "proxy": "http://58.253.156.159:9999",
        # }
        yield SplashRequest(url=url, callback=self.parse, args={"wait": 5})

    def parse(self, response):
        self.logger.info(response.text)
        # requests.get().status_code

    # def errback_f(self, failure):
    #     # 校验失败的处理
    #     if not failure.check(OpenSSL.SSL.Error, TimeoutError):
    #         self.logger.error("出现新的请求错误，请检查程序!!! {}".format(failure))
    #         self.logger.error(failure.request.meta)
    #         return

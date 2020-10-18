# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProxyipSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    proxy_ip = scrapy.Field()
    proxy_port = scrapy.Field()
    proxy_anonymity = scrapy.Field()
    proxy_type = scrapy.Field()
    proxy_response_speed = scrapy.Field()
    proxy = scrapy.Field()
    status = scrapy.Field()
    proxy_request_type = scrapy.Field()

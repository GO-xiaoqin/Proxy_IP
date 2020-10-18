# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy import settings
from itemadapter import ItemAdapter
from ProxyIP_Spider.tools.connect_redis import RedisPool


class ProxyipSpiderPipeline:

    def __init__(self, host, port, pwd):
        self.host = host
        self.port = port
        self.pwd = pwd

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get("REDIS_HOST"),
            port=crawler.settings.get("REDIS_PORT"),
            pwd=crawler.settings.get("REDIS_PWD"),
        )

    def open_spider(self, spider):
        spider.logger.info("Create redis instance")
        self.redis = RedisPool(self.host, self.port, self.pwd)

    def process_item(self, item, spider):
        if not item['proxy']:
            return
        field = "GET {} {}".format(item['proxy'], item['proxy_response_speed'])
        if "proxy_request_type" in item.keys():
            field = "GET/POST {} {}".format(item['proxy'], item['proxy_response_speed']) \
                if "POST" in item['proxy_request_type'] else field

        result = self.redis.check_proxy(field)
        if item['status']:
            # 代理可用
            spider.logger.info("The {} proxy available.".format(field))
            self.redis.add_one(field)
        else:
            # 代理不可用
            spider.logger.info("The {} proxy unavailable.".format(field))
            if not result:
                self.redis.del_proxy(field)
        return item

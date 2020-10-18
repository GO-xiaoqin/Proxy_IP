import random

import redis
import requests


class RedisPool(object):
    def __init__(self, host, port, password):
        redis_config = {
            "host": host,
            "port": port,
            "password": password,
        }
        self.pool = redis.ConnectionPool(**redis_config)
        self.redis = redis.StrictRedis(connection_pool=self.pool)

    def check_proxy(self, proxy, name="proxy"):
        """查询是否在redis"""
        result = self.redis.zscore(name, proxy)
        return result

    def add_one(self, proxy, name="proxy"):
        """为可用代理加分"""
        result = self.redis.zincrby(name=name, value=proxy, amount=1)
        return result

    def del_proxy(self, proxy, name="proxy"):
        """删除无效的代理"""
        result = self.redis.zrem(name, proxy)
        return result

    def get_proxy(self, name="proxy"):
        """获取一个可用的代理"""
        result = self.redis.zrange(name=name, start=0, end=-1, withscores=True)
        proxy_list = result[::-1] if result else []
        for i in proxy_list:
            proxy = i[0].decode('utf-8')
            proxies = dict()
            if "https" in str(proxy).split()[1].lower():
                proxies['https'] = str(proxy).split()[1]
            else:
                proxies['http'] = str(proxy).split()[1]
            try:
                timeout = int(str(proxy).split()[2])
            except ValueError:
                timeout = float(str(proxy).split()[2])
            except Exception:
                break

            r_url = ["http://httpbin.org/ip", "http://ip-api.com/json/?lang=zh-CN"]
            try:
                requests.get(url=random.choice(r_url), proxies=proxies, timeout=timeout)
            except Exception:
                self.del_proxy(i[0].decode('utf-8'))
            else:
                return proxy


if __name__ == "__main__":
    redis = RedisPool(
        "127.0.0.1",
        6379,
        "Xu551212"
    )
    # test = redis.check_proxy(proxy="bb", name="test")
    # test = redis.get_proxy()
    # print(test)

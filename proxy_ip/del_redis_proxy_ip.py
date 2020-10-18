# -*- coding: utf-8 -*- 
# date: 20-10-13 下午4:06

import redis


class RedisPool(object):
    def __init__(self, host, port, password):
        redis_config = {
            "host": host,
            "port": port,
            "password": password,
        }
        self.pool = redis.ConnectionPool(**redis_config)
        self.redis = redis.StrictRedis(connection_pool=self.pool)

    def del_proxy(self, scores, name="proxy"):
        """删除无效的代理"""
        result = self.redis.zremrangebyscore(name=name, min=0, max=scores)
        return result

    def get_proxy(self, name="proxy"):
        """获取一个可用的代理"""
        result = self.redis.zrange(name=name, start=0, end=-1, withscores=True)
        return result[-1] if result else None


if __name__ == "__main__":
    # 这是一个定时清理redis proxy 的一个脚本，定时任务在后台 crontab 里
    redis = RedisPool(
        "127.0.0.1",
        6379,
        "Xu551212"
    )
    result = redis.get_proxy()
    scores = int(result[1]) - 1 if result else 0
    redis.del_proxy(scores)


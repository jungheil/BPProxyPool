import json
from collections import defaultdict
from random import choice

from redis import Redis
from redis.connection import BlockingConnectionPool
from redis.exceptions import ConnectionError, ResponseError, TimeoutError

from handler.logger import LogHandler


class RedisClient(object):
    """
    Redis client

    Redis中代理存放的结构为hash：
    key为ip:port, value为代理属性的字典;

    """

    def __init__(self, **kwargs):
        self.name = ""
        kwargs.pop("username")
        self.__conn = Redis(
            connection_pool=BlockingConnectionPool(
                decode_responses=True, timeout=5, socket_timeout=5, **kwargs
            )
        )

    def get(self, protocol=[]):
        if isinstance(protocol, str):
            protocol = [protocol]
        if not isinstance(protocol, list):
            raise TypeError("protocol must be list")
        if len(protocol) > 0:
            items = self.__conn.hvals(self.name)
            proxies = list(
                filter(
                    lambda x: len(
                        set(protocol).intersection(set(json.loads(x).get("protocol")))
                    )
                    > 0,
                    items,
                )
            )
            return choice(proxies) if proxies else None
        else:
            proxies = self.__conn.hkeys(self.name)
            proxy = choice(proxies) if proxies else None
            return self.__conn.hget(self.name, proxy) if proxy else None

    def put(self, proxy_obj):
        data = self.__conn.hset(self.name, proxy_obj.addr, proxy_obj.to_json)
        return data

    def pop(self, protocol=[]):
        proxy = self.get(protocol)
        if proxy:
            self.__conn.hdel(self.name, json.loads(proxy).get("proxy", ""))
        return proxy if proxy else None

    def delete(self, addr):
        return self.__conn.hdel(self.name, addr)

    def exists(self, proxy_str):
        return self.__conn.hexists(self.name, proxy_str)

    def update(self, proxy_obj):
        return self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)

    def get_all(self, protocol=[]):
        items = self.__conn.hvals(self.name)
        if len(protocol) > 0:
            return list(
                filter(
                    lambda x: len(
                        set(protocol).intersection(set(json.loads(x).get("protocol")))
                    )
                    > 0,
                    items,
                )
            )
        else:
            return items

    def clear(self):
        return self.__conn.delete(self.name)

    def get_count(self):
        proxies = self.get_all()
        protocol_dict = defaultdict(int)
        source_dict = defaultdict(int)
        for proxy in proxies:
            proxy = json.loads(proxy)
            for ptc in proxy["protocol"]:
                protocol_dict[ptc] += 1
                source_dict[proxy["source"]] += 1
        return {"protocol": protocol_dict, "source": source_dict, "count": len(proxies)}

    def changeTable(self, name):
        self.name = name

    def test(self):
        log = LogHandler("redis_client")
        try:
            self.get_count()
        except TimeoutError as e:
            log.error("redis connection time out: %s", str(e), exc_info=True)
            return e
        except ConnectionError as e:
            log.error("redis connection error: %s", str(e), exc_info=True)
            return e
        except ResponseError as e:
            log.error("redis connection error: %s", str(e), exc_info=True)
            return e

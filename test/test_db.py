import unittest

from db.dbClient import DbClient
from helper.proxy import Proxy


class TestDB(unittest.TestCase):
    @unittest.skip("skip test redis")
    def test_redis(self):
        def check_proxy_equal(proxy1, proxy2):
            self.assertEqual(proxy1.addr, proxy2.addr)
            self.assertListEqual(proxy1.protocol, proxy2.protocol)
            self.assertEqual(proxy1.fail_count, proxy2.fail_count)
            self.assertEqual(proxy1.region, proxy2.region)
            self.assertEqual(proxy1.anonymous, proxy2.anonymous)
            self.assertEqual(proxy1.source, proxy2.source)
            self.assertEqual(proxy1.check_count, proxy2.check_count)
            self.assertEqual(proxy1.last_status, proxy2.last_status)
            self.assertEqual(proxy1.last_time, proxy2.last_time)

        db = DbClient("redis://@127.0.0.1:6379/0")
        db.change_table("test_db")
        proxy_dict = {
            "addr": "192.168.16.1:6666",
            "protocol": ["http", "https"],
            "fail_count": 6,
            "region": "CN",
            "anonymous": "",
            "source": "test_source",
            "check_count": 1,
            "last_status": True,
            "last_time": "2023-10-10 10:10:10",
        }
        proxy = Proxy(
            addr=proxy_dict["addr"],
            protocol=proxy_dict["protocol"],
            fail_count=proxy_dict["fail_count"],
            region=proxy_dict["region"],
            anonymous=proxy_dict["anonymous"],
            source=proxy_dict["source"],
            check_count=proxy_dict["check_count"],
            last_status=proxy_dict["last_status"],
            last_time=proxy_dict["last_time"],
        )
        db.put(proxy)
        get_proxy = Proxy.create_from_json(db.get(protocol=["scoks4", "https"]))
        check_proxy_equal(proxy, get_proxy)
        get_proxy = Proxy.create_from_json(db.get(protocol="http"))
        check_proxy_equal(proxy, get_proxy)
        self.assertIsNone(db.get(protocol="socks5"))
        self.assertTrue(db.exists(proxy.addr))
        self.assertFalse(db.exists("192.168.16.1:6667"))
        proxy_count = db.get_count()
        self.assertEqual(proxy_count["count"], 1)
        self.assertEqual(proxy_count["protocol"]["http"], 1)
        all_proxy = db.get_all()
        self.assertEqual(len(all_proxy), 1)
        check_proxy_equal(proxy, Proxy.create_from_json(all_proxy[0]))
        check_proxy_equal(
            proxy, Proxy.create_from_json(db.pop(protocol=["http", "https"]))
        )

import os
import unittest

from config import config


class TestConfig(unittest.TestCase):
    def test_get_env(self):
        os.environ["DB_CONN"] = "redis://@192.168.16.1:6666/0"
        os.environ["HOST"] = "192.168.16.1"
        os.environ["FETCH_PROTOCOL"] = "https,socks4,socks5"
        os.environ["VAL_SITES"] = "httpbin=httpbin.org,test=www.test.com"
        os.environ["FETCH_SEMAPHORE"] = "128"
        config.reset()
        config.get_env()
        self.assertEqual(config.db_config["db_conn"], "redis://@192.168.16.1:6666/0")
        self.assertEqual(config.server_config["host"], "192.168.16.1")
        self.assertListEqual(
            config.fetch_config["fetch_protocol"], ["https", "socks4", "socks5"]
        )
        self.assertDictEqual(
            config.fetch_config["val_sites"],
            {"httpbin": "httpbin.org", "test": "www.test.com"},
        )
        self.assertEqual(config.scheduler_config["fetch_semaphore"], 128)

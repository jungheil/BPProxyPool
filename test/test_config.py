import os
import unittest

from config import db_config, fetch_config, get_env, scheduler_config, server_config


class TestConfig(unittest.TestCase):
    def test_get_env(self):
        os.environ["DB_CONN"] = "redis://@192.168.16.1:6666/0"
        os.environ["HOST"] = "192.168.16.1"
        os.environ["VAL_HTTPS"] = "https://192.168.16.1"
        os.environ["FETCH_SEMAPHORE"] = "128"
        get_env()
        self.assertEqual(db_config["db_conn"], "redis://@192.168.16.1:6666/0")
        self.assertEqual(server_config["host"], "192.168.16.1")
        self.assertEqual(fetch_config["val_https"], "https://192.168.16.1")
        self.assertEqual(scheduler_config["fetch_semaphore"], 128)

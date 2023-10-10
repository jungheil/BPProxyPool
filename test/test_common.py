import json
import unittest

from helper.proxy import Proxy


class TestCommon(unittest.TestCase):
    def test_proxy(self):
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

        proxy = Proxy.create_from_json(json.dumps(proxy_dict))
        self.assertEqual(proxy.addr, proxy_dict["addr"])
        self.assertEqual(proxy.protocol, proxy_dict["protocol"])
        self.assertEqual(proxy.fail_count, proxy_dict["fail_count"])
        self.assertEqual(proxy.region, proxy_dict["region"])
        self.assertEqual(proxy.anonymous, proxy_dict["anonymous"])
        self.assertEqual(proxy.source, proxy_dict["source"])
        self.assertEqual(proxy.check_count, proxy_dict["check_count"])
        self.assertEqual(proxy.last_status, proxy_dict["last_status"])
        self.assertEqual(proxy.last_time, proxy_dict["last_time"])

        self.assertDictEqual(proxy.to_dict, proxy_dict)

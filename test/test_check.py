import asyncio
import unittest

from config import config
from helper.checker import do_validator
from helper.proxy import Proxy
from helper.validator import ValidatorRegistry, get_headers_validator


class TestValidator(unittest.TestCase):
    def test_fetch_protocol(self):
        config._fetch_config["val_sites"] = {}
        config._fetch_config["fetch_protocol"] = ["http", "socks5"]

        ValidatorRegistry.clear_instances()
        proxy_validator = ValidatorRegistry()

        @proxy_validator.add_validator("test_http", "http")
        def test_http_validator(proxy):
            pass

        @proxy_validator.add_validator("test_socks4", "socks4")
        def test_socks4_validator(proxy):
            pass

        @proxy_validator.add_validator("test_socks5", "socks5")
        def test_socks5_validator(proxy):
            pass

        protocol = proxy_validator.validators.keys()
        self.assertListEqual(list(protocol), ["http", "socks5"])

        self.assertDictEqual(
            proxy_validator.validators["http"],
            {"test_http": test_http_validator},
        )
        self.assertDictEqual(
            proxy_validator.validators["socks4"],
            {},
        )

    def test_undefined_protocol(self):
        config._fetch_config["fetch_protocol"] = ["https", "socks5", "undefined"]

        ValidatorRegistry.clear_instances()

        with self.assertRaises(ValueError):
            ValidatorRegistry()

        config._fetch_config["fetch_protocol"] = ["https", "socks5"]
        ValidatorRegistry.clear_instances()


class TestCheck(unittest.TestCase):
    def test_do_validator(self):
        config._fetch_config["fetch_protocol"] = ["http", "https", "socks4", "socks5"]

        ValidatorRegistry.clear_instances()
        vr = ValidatorRegistry()

        validator = get_headers_validator("www.httpbin.org", "http")
        vr.add_validator("http_test", "http")(validator)
        validator = get_headers_validator("www.httpbin.org", "https")
        vr.add_validator("https_test", "https")(validator)
        validator = get_headers_validator("www.httpbin.org", "socks4")
        vr.add_validator("socks4_test", "socks4")(validator)
        validator = get_headers_validator("www.httpbin.org", "socks5")
        vr.add_validator("socks5_test", "socks5")(validator)

        proxy = Proxy("127.0.0.1:8888")

        sem = asyncio.Semaphore(1)
        asyncio.run(do_validator(proxy, True, sem))

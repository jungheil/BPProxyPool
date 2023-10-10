import asyncio
import unittest

from config import fetch_config
from helper import checker, validator
from helper.proxy import Proxy


class TestValidator(unittest.TestCase):
    def test_fetch_protocol(self):
        fetch_config["fetch_protocol"] = ["http", "socks5"]

        validator.ValidatorRegistry.clear_instances()
        proxy_validator = validator.ValidatorRegistry()

        protocol = proxy_validator._protocol_validator.keys()
        self.assertListEqual(list(protocol), ["http", "socks5"])

        @proxy_validator.add_validator("http")
        def test_http_validator(proxy):
            pass

        @proxy_validator.add_validator("socks4")
        def test_socks4_validator(proxy):
            pass

        self.assertDictEqual(
            proxy_validator._protocol_validator,
            {
                "http": [test_http_validator],
                "socks5": [],
            },
        )

    def test_pre_validator(self):
        validator.ValidatorRegistry.clear_instances()
        proxy_validator = validator.ValidatorRegistry()

        @proxy_validator.add_validator("pre")
        def test_pre_validator(proxy):
            pass

        self.assertListEqual(
            proxy_validator._pre_validator,
            [test_pre_validator],
        )

    def test_undefined_protocol(self):
        fetch_config["fetch_protocol"] = ["https", "socks5", "undefined"]

        validator.ValidatorRegistry.clear_instances()

        with self.assertRaises(ValueError):
            validator.ValidatorRegistry()

        fetch_config["fetch_protocol"] = ["https", "socks5"]
        validator.ValidatorRegistry.clear_instances()


class TestCheck(unittest.TestCase):
    def test_do_validator(self):
        fetch_config["fetch_protocol"] = ["http", "https", "socks4", "socks5"]

        validator.ValidatorRegistry.clear_instances()
        proxy_checker = validator.ValidatorRegistry()

        proxy_checker.add_validator("pre")(validator.format_validator)
        proxy_checker.add_validator("http")(validator.http_timeout_validator)
        proxy_checker.add_validator("https")(validator.https_timeout_validator)
        proxy_checker.add_validator("socks4")(validator.socks4_timeout_validator)
        proxy_checker.add_validator("socks5")(validator.socks5_timeout_validator)

        proxy = Proxy("127.0.0.1:8888")

        sem = asyncio.Semaphore(1)
        asyncio.run(checker.do_validator(proxy, True, sem))

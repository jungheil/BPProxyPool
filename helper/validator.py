from collections import defaultdict

from curl_cffi import requests

from config import config
from utils.singleton import SingletonMeta


def get_headers_validator(url, ptc):
    async def warpper_validator(addr):
        proxies = {"http": f"{ptc}://{addr}", "https": f"{ptc}://{addr}"}
        async with requests.AsyncSession() as session:
            try:
                r = await session.head(
                    url,
                    proxies=proxies,
                    timeout=config.fetch_config["val_timeout"],
                )
                return True if r.status_code == 200 else False
            except Exception:
                return False

    return warpper_validator


class ValidatorRegistry(metaclass=SingletonMeta):
    def __init__(self) -> None:
        supported_protocol = set(["http", "https", "socks4", "socks5"])
        if not set(config.fetch_config["fetch_protocol"]).issubset(supported_protocol):
            raise ValueError(f"fetch_protocol should be one of {supported_protocol}")
        self._validators = defaultdict(dict)
        self._add_base_validator()

    @property
    def validators(self):
        return self._validators

    def _add_base_validator(self):
        for ptc in config.fetch_config["fetch_protocol"]:
            for site_name, site_url in config.fetch_config["val_sites"].items():
                if ptc == "http":
                    url = f"http://{site_url}"
                else:
                    url = f"https://{site_url}"
                if ptc == "https":
                    pptc = "http"
                else:
                    pptc = ptc
                validator = get_headers_validator(url, pptc)
                self.add_validator(site_name, ptc)(validator)

    def add_validator(self, val_name, ptc, required=False):
        ptc = ptc.lower()
        if ptc not in config.fetch_config["fetch_protocol"]:

            def ignore_warpper(func):
                return func

            return ignore_warpper
        if val_name in self._validators[ptc].keys():
            raise ValueError(f"validator {val_name} for protocol {ptc} already exists")

        def warpper(func):
            async def validator(addr):
                ret = await func(addr)
                return (ret, val_name, required)

            self._validators[ptc][val_name] = validator
            return validator

        return warpper

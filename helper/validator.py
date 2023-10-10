import re

from curl_cffi import requests

from config import fetch_config
from util.singleton import SingletonMeta


class ValidatorRegistry(metaclass=SingletonMeta):
    def __init__(self) -> None:
        supported_protocol = set(["http", "https", "socks4", "socks5"])
        if not set(fetch_config["fetch_protocol"]).issubset(supported_protocol):
            raise ValueError(f"fetch_protocol should be one of {supported_protocol}")
        self._pre_validator = []
        self._protocol_validator = {i: [] for i in fetch_config["fetch_protocol"]}

    @property
    def pre_validator(self):
        return self._pre_validator

    @property
    def protocol_validator(self):
        return self._protocol_validator

    def add_validator(self, val_type):
        val_type = val_type.lower()

        def warpper(func):
            if val_type == "pre":
                self._pre_validator.append(func)
            elif self._protocol_validator.get(val_type) is not None:
                self._protocol_validator[val_type].append(func)
            return func

        return warpper


IP_REGEX = re.compile(
    r"^((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.){3}(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])(?::(?:[0-9]|[1-9][0-9]{1,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5]))$"
)


@ValidatorRegistry().add_validator("pre")
async def format_validator(addr):
    """检查代理格式"""
    return True if IP_REGEX.fullmatch(addr) else False


@ValidatorRegistry().add_validator("http")
async def http_timeout_validator(addr):
    """http检测超时"""

    proxies = {"http": f"http://{addr}"}
    async with requests.AsyncSession() as session:
        try:
            r = await session.head(
                fetch_config["val_http"],
                proxies=proxies,
                timeout=fetch_config["val_timeout"],
                impersonate="chrome110",
            )
            return True if r.status_code == 200 else False
        except Exception as e:
            return False


@ValidatorRegistry().add_validator("https")
async def https_timeout_validator(addr):
    """https检测超时"""

    proxies = {"https": f"http://{addr}"}
    async with requests.AsyncSession() as session:
        try:
            r = await session.head(
                fetch_config["val_https"],
                proxies=proxies,
                timeout=fetch_config["val_timeout"],
                verify=fetch_config["verify"],
                impersonate="chrome110",
            )
            return True if r.status_code == 200 else False
        except Exception as e:
            return False


@ValidatorRegistry().add_validator("socks4")
async def socks4_timeout_validator(addr):
    """socks4检测超时"""
    proxies = {"https": f"socks4://{addr}"}
    async with requests.AsyncSession() as session:
        try:
            r = await session.head(
                fetch_config["val_https"],
                proxies=proxies,
                timeout=fetch_config["val_timeout"],
                verify=fetch_config["verify"],
                impersonate="chrome110",
            )
            return True if r.status_code == 200 else False
        except Exception as e:
            return False


@ValidatorRegistry().add_validator("socks5")
async def socks5_timeout_validator(addr):
    """socks5检测超时"""
    proxies = {"https": f"socks5://{addr}"}
    async with requests.AsyncSession() as session:
        try:
            r = await session.head(
                fetch_config["val_https"],
                proxies=proxies,
                timeout=fetch_config["val_timeout"],
                verify=fetch_config["verify"],
                impersonate="chrome110",
            )
            return True if r.status_code == 200 else False
        except Exception as e:
            return False

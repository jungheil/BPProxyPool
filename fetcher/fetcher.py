import asyncio
import base64
import re
import time

import execjs
from curl_cffi import requests
from lxml import etree

from config import config
from handler.logger import LogHandler
from utils.singleton import SingletonMeta

logger = LogHandler("fetcher")


class FetcherRegistry(metaclass=SingletonMeta):
    def __init__(self):
        self._fetchers = {}

    @property
    def fetchers(self):
        return self._fetchers

    def register(self, name):
        def wrapper(cls):
            if not issubclass(cls, Fetcher):
                raise TypeError(f"{cls.__name__} must be subclass of Fetcher")
            self._fetchers[name] = cls
            return cls

        return wrapper

    def get(self, name):
        return self._fetchers.get(name)

    def remove(self, name):
        return self._fetchers.pop(name, None)


class Fetcher:
    def __init__(self) -> None:
        self.name = "Unknown"
        self.last_run_time = int(time.time())
        self.delay = 0
        self.proxies = (
            {
                "http": config.fetch_config["fetch_proxy"],
                "https": config.fetch_config["fetch_proxy"],
            }
            if len(config.fetch_config["fetch_proxy"])
            else None
        )

    async def init_fetcher(self):
        pass

    async def fetcher(self):
        raise StopAsyncIteration

    async def __aenter__(self):
        try:
            await self.init_fetcher()
            return self
        except Exception:
            logger.error("init fetcher %s error", self.name)
            return Fetcher()

    async def __aexit__(self, exc_type, exc, tb):
        pass

    def __aiter__(self):
        return self

    async def __anext__(self):
        now_time = int(time.time())
        delay_time = self.delay - (now_time - self.last_run_time)
        if delay_time > 0:
            await asyncio.sleep(delay_time)
        try:
            ret = await self.fetcher()
            self.last_run_time = int(time.time())
            return ret
        except Exception as e:
            if not isinstance(e, StopAsyncIteration):
                logger.error("fetcher %s raise, msg: %s.", self.name, str(e))
            raise StopAsyncIteration from e


@FetcherRegistry().register("zdaye")
class FCzdaye(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "zdaye"
        self.delay = 10
        self.page_count = 10
        self.target_urls = []

    async def init_fetcher(self):
        target_url = "https://www.zdaye.com/free/{}/"
        self.target_urls = []
        for i in range(1, self.page_count + 1):
            self.target_urls.append(target_url.format(i))

    async def fetcher(self):
        try:
            url = self.target_urls.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "DNT": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }
        async with requests.AsyncSession() as session:
            response = await session.get(
                url,
                headers=headers,
                timeout=10,
                impersonate="chrome110",
                proxies=self.proxies,
            )
            tree = etree.HTML(response.text)
            data = tree.xpath('//*[@id="ipc"]/tbody/tr')
            ret = []
            for i in data:
                ip = i.xpath("./td[1]/text()")[0]
                port = i.xpath("./td[2]/text()")[0]
                ret.append(f"{ip}:{port}")
        return ret


@FetcherRegistry().register("fkxdaili")
class FCfkxdaili(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "fkxdaili"
        self.page_count = 10
        self.delay = 2
        self.target_urls = []

    async def init_fetcher(self):
        target_url = "http://www.kxdaili.com/dailiip/{}/{}.html"
        self.target_urls = []
        for tabIndex in range(2):
            for pageIndex in range(self.page_count):
                self.target_urls.append(target_url.format(tabIndex + 1, pageIndex + 1))

    async def fetcher(self):
        try:
            url = self.target_urls.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        async with requests.AsyncSession() as session:
            response = await session.get(
                url, timeout=10, impersonate="chrome110", proxies=self.proxies
            )
        tree = etree.HTML(response.text)
        ret = []
        for tr in tree.xpath("//table[@class='active']//tr")[1:]:
            ip = "".join(tr.xpath("./td[1]/text()")).strip()
            port = "".join(tr.xpath("./td[2]/text()")).strip()
            ret.append("%s:%s" % (ip, port))
        return ret


@FetcherRegistry().register("fkuaidaili")
class FCfkuaidaili(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "fkuaidaili"
        self.page_count = 10
        self.delay = 10
        self.target_urls = []

    async def init_fetcher(self):
        url_pattern = [
            "https://www.kuaidaili.com/free/inha/{}/",
            "https://www.kuaidaili.com/free/intr/{}/",
        ]
        for page_index in range(self.page_count):
            for pattern in url_pattern:
                self.target_urls.append(pattern.format(page_index + 1))

    async def fetcher(self):
        try:
            url = self.target_urls.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        async with requests.AsyncSession() as session:
            response = await session.get(
                url, timeout=10, impersonate="chrome110", proxies=self.proxies
            )
        tree = etree.HTML(response.text)
        proxy_list = tree.xpath(".//table//tr")
        ret = []
        for tr in proxy_list[1:]:
            ret.append(":".join(tr.xpath("./td/text()")[0:2]))
        return ret


@FetcherRegistry().register("fip3366")
class FCfip3366(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "fip3366"
        self.delay = 2
        self.target_urls = []

    async def init_fetcher(self):
        self.target_urls = [
            "http://www.ip3366.net/free",
        ]

    async def fetcher(self):
        try:
            url = self.target_urls.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        async with requests.AsyncSession() as session:
            response = await session.get(
                url, timeout=10, impersonate="chrome110", proxies=self.proxies
            )
            proxies = re.findall(
                r"<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>",
                response.content.decode("utf-8", errors="ignore"),
            )
            ret = [":".join(proxy) for proxy in proxies]
            return ret


@FetcherRegistry().register("f89ip")
class FCf89ip(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "f89ip"
        self.page_count = 10
        self.delay = 10
        self.target_urls = []

    async def init_fetcher(self):
        target_url = "https://www.89ip.cn/index_{}.html"
        for page_index in range(1, self.page_count + 1):
            self.target_urls.append(target_url.format(page_index))

    async def fetcher(self):
        try:
            url = self.target_urls.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        async with requests.AsyncSession() as session:
            response = await session.get(
                url, timeout=10, impersonate="chrome110", proxies=self.proxies
            )
        proxies = re.findall(
            r"<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>",
            response.text,
        )
        ret = [":".join(proxy) for proxy in proxies]
        return ret


@FetcherRegistry().register("docip")
class FCdocip(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "docip"
        self.target_urls = []

    async def init_fetcher(self):
        self.target_urls = ["https://www.docip.net/data/free.json"]

    async def fetcher(self):
        try:
            url = self.target_urls.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        async with requests.AsyncSession() as session:
            response = await session.get(
                url, timeout=10, impersonate="chrome110", proxies=self.proxies
            )
        ret = [i["ip"] for i in response.json()["data"]]
        return ret


@FetcherRegistry().register("pzzqz")
class FCpzzqz(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "pzzqz"
        self.delay = 2
        self.target_region = []
        self.cookies = None
        self.headers = None

    async def init_fetcher(self):
        self.target_region = ["cn", "hk", "gb", "us", "sg"]
        async with requests.AsyncSession() as session:
            response = await session.get(
                "https://pzzqz.com/",
                timeout=10,
                impersonate="chrome110",
                proxies=self.proxies,
            )
            x_csrf_token = re.findall('X-CSRFToken": "(.*?)"', response.text)
            self.cookies = session.cookies
            self.headers = {"X-CSRFToken": x_csrf_token[0]}

    async def fetcher(self):
        try:
            rg = self.target_region.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        async with requests.AsyncSession() as session:
            data = {
                "http": "on",
                "socks5": "on",
                "ping": "1000",
                "country": rg,
                "ports": "",
            }
            response = await session.post(
                "https://pzzqz.com/",
                json=data,
                timeout=10,
                impersonate="chrome110",
                headers=self.headers,
                cookies=self.cookies,
                proxies=self.proxies,
            )
            tree = etree.HTML(response.text)
            ret = []
            for tr in tree.xpath("//tr"):
                ip = "".join(tr.xpath("./td[1]/text()"))
                port = "".join(tr.xpath("./td[2]/text()"))
                ret.append("%s:%s" % (ip, port))
            return ret


@FetcherRegistry().register("geonode")
class FCgeonode(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "geonode"
        self.page_count = 5
        self.delay = 2
        self.page = []

    async def init_fetcher(self):
        self.page = [i for i in range(1, self.page_count + 1)]

    async def fetcher(self):
        try:
            page = self.page.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        headers = {
            "authority": "proxylist.geonode.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "dnt": "1",
            "origin": "https://geonode.com",
            "referer": "https://geonode.com/",
        }
        params = {
            "limit": "100",
            "page": f"{page}",
            "sort_by": "lastChecked",
            "sort_type": "desc",
        }
        async with requests.AsyncSession() as session:
            response = await session.get(
                "https://proxylist.geonode.com/api/proxy-list",
                params=params,
                headers=headers,
                timeout=10,
                impersonate="chrome110",
                proxies=self.proxies,
            )
            data = response.json()["data"]
            ret = [f'{i["ip"]}:{i["port"]}' for i in data]
        return ret


@FetcherRegistry().register("fpcz")
class FCfpcz(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "fpcz"
        self.page_count = 5
        self.delay = 2
        self.target_urls = []

    async def init_fetcher(self):
        self.target_urls = []
        target_url = "http://free-proxy.cz/en/proxylist/main/{}"
        for page_index in range(self.page_count):
            self.target_urls.append(target_url.format(page_index + 1))
        self.target_urls = self.target_urls[::-1]

    async def fetcher(self):
        try:
            url = self.target_urls.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "DNT": "1",
            "Proxy-Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        async with requests.AsyncSession() as session:
            response = await session.get(
                url,
                timeout=10,
                impersonate="chrome110",
                headers=headers,
                proxies=self.proxies,
            )
        tree = etree.HTML(response.text)
        data = tree.xpath('//table[@id="proxy_list"]/tbody/tr')
        ret = []
        for i in data:
            try:
                ip_script = i.xpath("./td[1]/script/text()")[0]
                ip = base64.b64decode(ip_script.split('"')[1]).decode("utf-8")
                port = i.xpath("./td[2]/span/text()")[0]
                ret.append(f"{ip}:{port}")
            except Exception:
                continue
        return ret


@FetcherRegistry().register("proxyscrape")
class FCproxyscrape(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "proxyscrape"
        self.target_urls = []

    async def init_fetcher(self):
        self.target_urls = ["https://api.proxyscrape.com/proxytable.php"]

    async def fetcher(self):
        try:
            url = self.target_urls.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        headers = {
            "authority": "api.proxyscrape.com",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "dnt": "1",
            "origin": "https://proxyscrape.com",
            "referer": "https://proxyscrape.com/",
        }
        params = {
            "nf": "true",
            "country": "all",
        }
        async with requests.AsyncSession() as session:
            response = await session.get(
                url,
                params=params,
                timeout=10,
                impersonate="chrome110",
                headers=headers,
                proxies=self.proxies,
            )
        ret = []
        for protocol in response.json().values():
            for proxy in protocol.keys():
                ret.append(proxy)
        return ret


@FetcherRegistry().register("fplnet")
class FCfplnet(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "fplnet"
        self.target_urls = []

    async def init_fetcher(self):
        self.target_urls = ["https://free-proxy-list.net/"]

    async def fetcher(self):
        try:
            url = self.target_urls.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        headers = {
            "authority": "free-proxy-list.net",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "dnt": "1",
            "referer": "https://www.google.com/",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }

        async with requests.AsyncSession() as session:
            response = await session.get(
                url,
                timeout=10,
                impersonate="chrome110",
                headers=headers,
                proxies=self.proxies,
            )
        tree = etree.HTML(response.text)
        data = tree.xpath('//*[@id="list"]/div/div[2]/div/table/tbody/tr')
        ret = []
        for i in data:
            try:
                ip = i.xpath("./td[1]/text()")[0]
                port = i.xpath("./td[2]/text()")[0]
                ret.append(f"{ip}:{port}")
            except Exception:
                continue
        return ret


@FetcherRegistry().register("hidemy")
class FChidemy(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "hidemy"
        self.target_urls = []

    async def init_fetcher(self):
        self.target_urls = ["https://hidemy.io/en/proxy-list/"]

    async def fetcher(self):
        try:
            url = self.target_urls.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        headers = {
            "authority": "hidemy.io",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "dnt": "1",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }

        async with requests.AsyncSession() as session:
            response = await session.get(
                url,
                timeout=10,
                impersonate="chrome110",
                headers=headers,
                proxies=self.proxies,
            )
        tree = etree.HTML(response.text)
        data = tree.xpath("/html/body/div[1]/div[4]/div/div[4]/table/tbody/tr")
        ret = []
        for i in data:
            try:
                ip = i.xpath("./td[1]/text()")[0]
                port = i.xpath("./td[2]/text()")[0]
                ret.append(f"{ip}:{port}")
            except Exception:
                continue
        return ret


@FetcherRegistry().register("openproxyspace")
class FCopenproxyspace(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "openproxyspace"
        self.delay = 2
        self.target_urls = []

    async def init_fetcher(self):
        self.target_urls = [
            "https://api.openproxy.space/lists/http",
            "https://api.openproxy.space/lists/socks4",
            "https://api.openproxy.space/lists/socks5",
        ]

    async def fetcher(self):
        try:
            url = self.target_urls.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        headers = {
            "authority": "openproxy.space",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }
        async with requests.AsyncSession() as session:
            response = await session.get(
                url,
                timeout=10,
                impersonate="chrome110",
                headers=headers,
                proxies=self.proxies,
            )
        data = response.json()["data"]
        ret = []
        for i in data:
            ret.extend(i["items"])
        return ret


@FetcherRegistry().register("proxynova")
class FCproxynova(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "proxynova"
        self.delay = 2
        self.target_urls = []

    async def init_fetcher(self):
        self.target_urls = [
            "https://www.proxynova.com/proxy-server-list/country-cn/",
            "https://www.proxynova.com/proxy-server-list/country-ru/",
            "https://www.proxynova.com/proxy-server-list/country-id/",
            "https://www.proxynova.com/proxy-server-list/country-co/",
            "https://www.proxynova.com/proxy-server-list/country-ar/",
        ]

    async def fetcher(self):
        try:
            url = self.target_urls.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        headers = {
            "authority": "www.proxynova.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "dnt": "1",
            "referer": "https://www.proxynova.com/",
            "upgrade-insecure-requests": "1",
        }
        async with requests.AsyncSession() as session:
            response = await session.get(
                url,
                timeout=10,
                impersonate="chrome110",
                headers=headers,
                proxies=self.proxies,
            )
        tree = etree.HTML(response.text)
        data = tree.xpath('//table[@id="tbl_proxy_list"]/tbody/tr')
        ret = []
        for i in data:
            try:
                ip_script = i.xpath(
                    "./td[1]/abbr/script/text() | ./td[1]/script/text()"
                )[0].strip()[15:-1]
                ip = execjs.eval(ip_script)
                port = i.xpath("./td[2]/text()")[0].strip()
                if not port:
                    port = i.xpath("./td[2]/a/text()")[0].strip()
                ret.append(f"{ip}:{port}")
            except Exception:
                continue
        return ret


@FetcherRegistry().register("spysone")
class FCspysone(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "spysone"
        self.target_urls = []

    async def init_fetcher(self):
        self.target_urls = [
            "https://spys.one/en/http-proxy-list/",
        ]

    async def fetcher(self):
        try:
            url = self.target_urls.pop()
        except IndexError as e:
            raise StopAsyncIteration from e

        headers = {
            "authority": "spys.one",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            "dnt": "1",
            "origin": "https://spys.one",
            "referer": "https://spys.one/en/http-proxy-list/",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }
        data = {
            "xx0": "",
            "xpp": "5",
            "xf1": "0",
            "xf2": "0",
            "xf4": "0",
            "xf5": "0",
        }

        async with requests.AsyncSession() as session:
            response = await session.get(
                url, timeout=10, impersonate="chrome110", proxies=self.proxies
            )
            tree = etree.HTML(response.text)
            data["xx0"] = tree.xpath('//input[@name="xx0"]/@value')[0]
            response = await session.post(
                url,
                data=data,
                timeout=10,
                impersonate="chrome110",
                headers=headers,
                proxies=self.proxies,
            )
            tree = etree.HTML(response.text)
            data["xx0"] = tree.xpath('//input[@name="xx0"]/@value')[0]
            response = await session.post(
                url,
                data=data,
                timeout=10,
                impersonate="chrome110",
                headers=headers,
                proxies=self.proxies,
            )
            tree = etree.HTML(response.text)
            env_script = tree.xpath("/html/body/script/text()")[0]
            ctx = execjs.compile(env_script)
            data = tree.xpath("//tr/td[1]/font")
            ret = []
            for i in data:
                try:
                    ip = i.xpath("./text()")[0]
                    port_script = i.xpath("./script/text()")[0]
                    port_script = port_script[port_script.find("+") : -1]
                    port = ctx.eval(f'""{port_script}')
                    ret.append(f"{ip}:{port}")
                except Exception:
                    continue
            return ret


@FetcherRegistry().register("pldl")
class FCpldl(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "pldl"
        self.delay = 2
        self.protocol = []

    async def init_fetcher(self):
        self.protocol = ["http", "https", "socks4", "socks5"]

    async def fetcher(self):
        try:
            protocol = self.protocol.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        async with requests.AsyncSession() as session:
            response = await session.get(
                "https://www.proxy-list.download/api/v1/get",
                params={"type": protocol},
                timeout=10,
                impersonate="chrome110",
                proxies=self.proxies,
            )
        data = response.text
        ret = data.split("\r\n")[:-1]
        return ret


@FetcherRegistry().register("xsdaili")
class FCxsdaili(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "xsdaili"
        self.page_num = 5
        self.target_urls = []
        self.delay = 2

    async def init_fetcher(self):
        async with requests.AsyncSession() as session:
            response = await session.get(
                "https://www.xsdaili.cn/",
                timeout=10,
                impersonate="chrome110",
                proxies=self.proxies,
            )
            tree = etree.HTML(response.text)
            data = tree.xpath('//div[@class="col-md-12"]/div/div/a/@href')
            self.target_urls = [
                "https://www.xsdaili.cn" + data[i] for i in range(self.page_num)
            ]

    async def fetcher(self):
        try:
            url = self.target_urls.pop()
        except IndexError as e:
            raise StopAsyncIteration from e
        async with requests.AsyncSession() as session:
            response = await session.get(
                url, timeout=10, impersonate="chrome110", proxies=self.proxies
            )
        tree = etree.HTML(response.text)
        data = tree.xpath('//div[@class="col-md-12"]/div[@class="cont"]/text()')
        ret = [i.strip().split("@")[0] for i in data]
        return ret


@FetcherRegistry().register("plorg")
class FCplorg(Fetcher):
    def __init__(self) -> None:
        super().__init__()
        self.name = "plorg"
        self.delay = 2
        self.page_count = 10
        self.target_urls = []

    async def init_fetcher(self):
        target_url = "https://proxy-list.org/english/index.php?p={}"
        self.target_urls = []
        for i in range(1, self.page_count + 1):
            self.target_urls.append(target_url.format(i))

    async def fetcher(self):
        try:
            url = self.target_urls.pop()
        except Exception as e:
            raise StopAsyncIteration from e
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "DNT": "1",
            "Referer": "https://proxy-list.org/english/index.php?p=1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }
        async with requests.AsyncSession() as session:
            response = await session.get(
                url,
                headers=headers,
                timeout=10,
                impersonate="chrome110",
                proxies=self.proxies,
            )
            tree = etree.HTML(response.text)
            data = tree.xpath(
                '//*[@id="proxy-table"]/div[2]/div/ul/li[1]/script/text()'
            )
            ret = [base64.b64decode(i[7:-2]).decode() for i in data]
        return ret


# TODO "https://ip.ihuan.me/"

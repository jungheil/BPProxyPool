import asyncio
from collections import defaultdict
from datetime import datetime

from curl_cffi import requests

from config import fetch_config
from handler.db_handler import DBHandler
from handler.logger import LogHandler
from helper.validator import ValidatorRegistry


async def regionGetter(proxy):
    try:
        url = (
            "https://searchplugin.csdn.net/api/v1/ip/get?ip=%s"
            % proxy.addr.split(":")[0]
        )
        async with requests.AsyncSession() as session:
            r = await session.get(url=url, retry_time=1, timeout=2)
        return r.json()["data"]["address"]
    except:
        return ""


async def do_validator(proxy, get_region, sem):
    async with sem:
        pre_check = await asyncio.gather(
            *[vld(proxy.addr) for vld in ValidatorRegistry()._pre_validator]
        )
        if all(pre_check):
            fut = defaultdict(list)
            for protocol, validators in ValidatorRegistry()._protocol_validator.items():
                fut[protocol] = asyncio.gather(*[vld(proxy.addr) for vld in validators])
            protocol_status = defaultdict(bool)
            for protocol, validators in fut.items():
                protocol_status[protocol] = all(await validators)

            status = any(protocol_status.values())
        else:
            status = False

        proxy.check_count += 1
        proxy.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        proxy.last_status = status
        if status:
            proxy.protocol = [k for k, v in protocol_status.items() if v]
            if proxy.fail_count > 0:
                proxy.fail_count -= 1
            if get_region:
                proxy.region = (
                    await regionGetter(proxy.addr) if fetch_config["get_region"] else ""
                )
        else:
            proxy.fail_count += 1
        return proxy


logger = LogHandler("checker")
proxy_handler = DBHandler()


async def proxy_checker(proxies, is_raw, sem):
    def _ifRaw(proxy):
        if proxy.last_status:
            if proxy_handler.exists(proxy):
                logger.info("RawCheck %s %s exist", proxy.source, proxy.addr.ljust(23))
            else:
                logger.info("RawCheck %s %s pass", proxy.source, proxy.addr.ljust(23))
                proxy_handler.put(proxy)
        else:
            logger.info("RawCheck %s %s failed", proxy.source, proxy.addr.ljust(23))

    def _ifUse(proxy):
        if proxy.last_status:
            logger.info("UseCheck %s %s pass", proxy.source, proxy.addr.ljust(23))
            proxy_handler.put(proxy)
        else:
            if proxy.fail_count > fetch_config["recheck_failed_count"]:
                logger.info(
                    "UseCheck %s %s fail, count %s delete",
                    proxy.source,
                    proxy.addr.ljust(23),
                    proxy.fail_count,
                )
                proxy_handler.delete(proxy)
            else:
                logger.info(
                    "UseCheck %s %s fail, count %s keep",
                    proxy.source,
                    proxy.addr.ljust(23),
                    proxy.fail_count,
                )
                proxy_handler.put(proxy)

    update_proxy = _ifRaw if is_raw else _ifUse
    fut = [asyncio.ensure_future(do_validator(proxy, is_raw, sem)) for proxy in proxies]
    for i in fut:
        proxy = await i
        update_proxy(proxy)

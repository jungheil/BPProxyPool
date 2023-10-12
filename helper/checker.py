import asyncio
from collections import defaultdict
from datetime import datetime

from curl_cffi import requests

from config import config
from handler.db_handler import DBHandler
from handler.logger import LogHandler
from helper.validator import ValidatorRegistry


async def get_ip_info(addr):
    try:
        url = f"http://ip-api.com/json/{addr.split(':')[0]}"
        async with requests.AsyncSession() as session:
            r = await session.get(
                url=url,
                timeout=5,
                impersonate="chrome110",
            )
        info = r.json()
        return f"{info['countryCode']} {info['region']}", f"{info['as']}"
    except Exception:
        return "", ""


async def do_validator(proxy, is_raw, sem):
    vr = ValidatorRegistry()
    async with sem:
        fut_dict = defaultdict(list)

        for k, v in vr.validators.items():
            fut_dict[k] = asyncio.gather(*[vld(proxy.addr) for vld in v.values()])

        protocol_status = defaultdict(bool)
        protocol_accessibility = defaultdict(dict)
        for protocol, fut in fut_dict.items():
            ret = await fut
            req_list = [i[0] for i in ret if i[2]]
            if len(req_list) == 0:
                protocol_status[protocol] = any([i[0] for i in ret if not i[2]])
            else:
                protocol_status[protocol] = all(req_list)
            for i in ret:
                protocol_accessibility[protocol][i[1]] = i[0]

        status = any(protocol_status.values())

        proxy.check_count += 1
        proxy.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        proxy.last_status = status
        if status:
            proxy.accessibility = {}
            for ptc, s in protocol_status.items():
                if s:
                    proxy.accessibility[ptc] = protocol_accessibility[ptc]
            if proxy.fail_count > 0:
                proxy.fail_count -= 1
            if is_raw and config.fetch_config["get_ip_info"]:
                proxy.region, proxy.asn = await get_ip_info(proxy.addr)

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
            if proxy.fail_count > config.fetch_config["recheck_failed_count"]:
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

import asyncio

from config import config
from fetcher import FetcherRegistry
from handler.logger import LogHandler
from helper.checker import proxy_checker
from helper.proxy import Proxy

logger = LogHandler("fetcher")


async def run_single_fetch(fetcher_name, sem):
    async with sem:
        fetcher = FetcherRegistry().get(fetcher_name)
        if fetcher is None:
            logger.error(f"%s not found", fetcher_name)
            return
        logger.info("%s start", fetcher_name)
        fut = []
        async with fetcher() as fc:
            async for proxies in fc:
                ret = []
                for i in proxies:
                    try:
                        ret.append(Proxy(i, source=fc.name))
                    except AssertionError:
                        continue
                fut.append(asyncio.ensure_future(proxy_checker(ret, True, sem)))
        for i in fut:
            await i
        logger.info("%s complete", fetcher_name)


async def run_fetch(sem):
    task = [run_single_fetch(i, sem) for i in config.fetch_config["fetchers"]]
    fut = asyncio.gather(*task)
    await fut

import asyncio
import time

from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler

from config import config
from handler.db_handler import DBHandler
from handler.logger import LogHandler
from helper.checker import proxy_checker
from helper.fetch import run_fetch

logger = LogHandler("scheduler")


class RunFetch:
    def __init__(self) -> None:
        self._last_run_time = int(time.time())
        self._proxy_handler = DBHandler()

    def __call__(self, force_run=False) -> None:
        now_time = int(time.time())
        interval = now_time - self._last_run_time
        logger.info("Checking if fetch is required.")
        if (
            force_run
            or interval >= 60 * config.scheduler_config["max_fetch_interval"]
            or self._proxy_handler.db.get_count().get("count", 0)
            < config.fetch_config["min_pool_size"]
        ):
            logger.info("Starting fetch.")
            sem = asyncio.Semaphore(config.scheduler_config["fetch_semaphore"])
            asyncio.run(run_fetch(sem))
            self._last_run_time = now_time
            logger.info("Fetch completed.")


class RunRecheck:
    def __init__(self) -> None:
        self._proxy_handler = DBHandler()

    def __call__(self) -> None:
        logger.info("Starting recheck.")
        proxies = self._proxy_handler.get_all()
        sem = asyncio.Semaphore(config.scheduler_config["recheck_semaphore"])
        asyncio.run(proxy_checker(proxies, False, sem))
        logger.info("Recheck completed.")


_run_proxy_fetch = RunFetch()
_run_proxy_check = RunRecheck()


def RunScheduler():
    timezone = config.scheduler_config["timezone"]
    scheduler_log = LogHandler("scheduler")
    scheduler = BlockingScheduler(logger=scheduler_log, timezone=timezone)

    executors = {
        "default": ThreadPoolExecutor(5),
        "processpool": ProcessPoolExecutor(5),
    }

    scheduler.configure(executors=executors, timezone=timezone)
    scheduler.add_job(
        _run_proxy_fetch,
        "interval",
        minutes=config.scheduler_config["run_fetch_interval"],
        coalesce=True,
        id="proxy_fetch",
        name="proxy fetch",
    )
    scheduler.add_job(
        _run_proxy_check,
        "interval",
        minutes=config.scheduler_config["run_recheck_interval"],
        coalesce=True,
        id="proxy_check",
        name="proxy recheck",
    )

    _run_proxy_fetch(True)
    scheduler.start()

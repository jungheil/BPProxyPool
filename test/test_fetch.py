import asyncio
import unittest

from fetcher import FetcherRegistry
from fetcher.fetcher import Fetcher
from helper.fetch import run_single_fetch


class TestFetch(unittest.TestCase):
    def test_fetcher_registry(self):
        with self.assertRaises(TypeError):
            FetcherRegistry().register("test")(object)
        self.assertIsNone(FetcherRegistry().get("test_undefined_name"))
        FetcherRegistry().register("test_fetcher")(Fetcher)
        self.assertEqual(FetcherRegistry().get("test_fetcher"), Fetcher)
        FetcherRegistry().remove("test_fetcher")

    def test_fetcher_stop_iter(self):
        for F in FetcherRegistry().fetchers.values():
            f = F()
            with self.assertRaises(StopAsyncIteration):
                asyncio.run(f.fetcher())

    def test_single_fetch(self):
        FetcherRegistry().register("test_fetcher")(Fetcher)
        from helper.fetch import logger

        logger.setLevel(50)
        asyncio.run(run_single_fetch("test_fetcher", asyncio.Semaphore(1)))
        FetcherRegistry().remove("test_fetcher")

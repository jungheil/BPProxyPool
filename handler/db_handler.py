from config import config
from db.dbClient import DbClient
from helper.proxy import Proxy


class DBHandler:
    def __init__(self):
        self.db = DbClient(config.db_config["db_conn"])
        self.db.change_table(config.db_config["table_name"])

    def get(self, protocol=[]):
        proxy = self.db.get(protocol)
        return Proxy.create_from_json(proxy) if proxy else None

    def pop(self, protocol=[]):
        proxy = self.db.pop(protocol)
        if proxy:
            return Proxy.create_from_json(proxy)
        return None

    def put(self, proxy):
        self.db.put(proxy)

    def delete(self, proxy):
        return self.db.delete(proxy.addr)

    def get_all(self, protocol=[]):
        proxies = self.db.get_all(protocol)
        return [Proxy.create_from_json(_) for _ in proxies]

    def get_count(self):
        return self.db.get_count()

    def exists(self, proxy):
        return self.db.exists(proxy.addr)

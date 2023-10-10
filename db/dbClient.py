import os
import sys
from urllib.parse import urlparse

from util.singleton import SingletonMeta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class DbClient(metaclass=SingletonMeta):  
    def __init__(self, db_conn):
        self.parse_db_conn(db_conn)
        self.__init_db_client()

    @classmethod
    def parse_db_conn(cls, db_conn):
        db_conf = urlparse(db_conn)
        cls.db_type = db_conf.scheme.upper().strip()
        cls.db_host = db_conf.hostname
        cls.db_port = db_conf.port
        cls.db_user = db_conf.username
        cls.db_pwd = db_conf.password
        cls.db_name = db_conf.path[1:]
        return cls

    def __init_db_client(self):
        __type = None
        if "SSDB" == self.db_type:
            __type = "ssdbClient"
        elif "REDIS" == self.db_type:
            __type = "redisClient"
        else:
            pass
        assert __type, f"type error, Not support DB type: {self.db_type}"
        self.client = getattr(__import__(__type), f"{self.db_type.title()}Client")(
            host=self.db_host,
            port=self.db_port,
            username=self.db_user,
            password=self.db_pwd,
            db=self.db_name,
        )

    def get(self, protocol, **kwargs):
        return self.client.get(protocol, **kwargs)

    def put(self, key, **kwargs):
        return self.client.put(key, **kwargs)

    def update(self, key, value, **kwargs):
        return self.client.update(key, value, **kwargs)

    def delete(self, key, **kwargs):
        return self.client.delete(key, **kwargs)

    def exists(self, key, **kwargs):
        return self.client.exists(key, **kwargs)

    def pop(self, protocol, **kwargs):
        return self.client.pop(protocol, **kwargs)

    def get_all(self, protocol=[]):
        return self.client.get_all(protocol)

    def clear(self):
        return self.client.clear()

    def change_table(self, name):
        self.client.changeTable(name)

    def get_count(self):
        return self.client.get_count()

    def test(self):
        return self.client.test()

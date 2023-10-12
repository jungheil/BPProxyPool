from utils.singleton import SingletonMeta

common_config = {
    "banner": r"""
 ____  ____  ____                      ____             _
| __ )|  _ \|  _ \ _ __ _____  ___   _|  _ \ ___   ___ | |
|  _ \| |_) | |_) | '__/ _ \ \/ / | | | |_) / _ \ / _ \| |
| |_) |  __/|  __/| | | (_) >  <| |_| |  __/ (_) | (_) | |
|____/|_|   |_|   |_|  \___/_/\_\\__, |_|   \___/ \___/|_|
                                 |___/
                                 
""",
    "version": "3.0.0",
}

db_config = {
    "db_conn": "redis://@127.0.0.1:6379/0",
    "table_name": "proxy",
}

server_config = {"host": "0.0.0.0", "port": 5010}

fetch_config = {
    "fetchers": [
        "zdaye",
        "fkxdaili",
        "fkuaidaili",
        "fip3366",
        "f89ip",
        "docip",
        "pzzqz",
        "geonode",
        "fpcz",
        "proxyscrape",
        "fplnet",
        "hidemy",
        "openproxyspace",
        "proxynova",
        "spysone",
        "pldl",
        "xsdaili",
        "plorg",
    ],
    "fetch_proxy": "",
    "val_timeout": 5,
    "recheck_failed_count": 2,
    "min_pool_size": 50,
    "get_ip_info": True,
    "val_sites": {
        "httpbin": "httpbin.org",
        "baidu": "www.baidu.com",
        "google": "www.google.com",
    },
    "fetch_protocol": ["https", "socks4", "socks5"],
}

scheduler_config = {
    "timezone": "Asia/Shanghai",
    "run_fetch_interval": 1,
    "max_fetch_interval": 60,
    "run_recheck_interval": 20,
    "fetch_semaphore": 32,
    "recheck_semaphore": 16,
}


class Config(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.reset()
        self.get_env()

    @property
    def common_config(self):
        return self._common_config

    @property
    def db_config(self):
        return self._db_config

    @property
    def server_config(self):
        return self._server_config

    @property
    def fetch_config(self):
        return self._fetch_config

    @property
    def scheduler_config(self):
        return self._scheduler_config

    def __str__(self) -> str:
        ret = f"{self._common_config['banner']}\n\nversion: {self._common_config['version']}\n"
        ret += "-- db_config:\n"
        for k, v in self._db_config.items():
            ret += f"    {k}: {v}\n"
        ret += "-- server_config:\n"
        for k, v in self._server_config.items():
            ret += f"    {k}: {v}\n"
        ret += "-- fetch_config:\n"
        for k, v in self._fetch_config.items():
            ret += f"    {k}: {v}\n"
        ret += "-- scheduler_config:\n"
        for k, v in self._scheduler_config.items():
            ret += f"    {k}: {v}\n"
        return ret

    def reset(self):
        self._common_config = common_config.copy()
        self._db_config = db_config.copy()
        self._server_config = server_config.copy()
        self._fetch_config = fetch_config.copy()
        self._scheduler_config = scheduler_config.copy()

    def get_env(self):
        import os

        for config in [
            self._db_config,
            self._server_config,
            self._fetch_config,
            self._scheduler_config,
        ]:
            config.update(
                {
                    k: self.cast_env(os.environ.get(k.upper(), v), v)
                    for k, v in config.items()
                }
            )

    @classmethod
    def cast_env(cls, env_str, target):
        target_type = type(target)
        if isinstance(env_str, target_type):
            return env_str
        if target_type == list:
            if len(target) == 0:
                return env_str.split(",")
            else:
                return [cls.cast_env(i, target[0]) for i in env_str.split(",")]
        elif target_type == dict:
            if len(target) == 0:
                return dict([i.split("=") for i in env_str.split(",")])
            else:
                tk = next(iter(target.keys()))
                tv = next(iter(target.values()))
                return dict(
                    [
                        [cls.cast_env(k, tk), cls.cast_env(v, tv)]
                        for k, v in [i.split("=") for i in env_str.split(",")]
                    ]
                )
        else:
            return target_type(env_str)


config = Config()

__all__ = ["config"]

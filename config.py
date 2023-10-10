def get_env():
    import os

    for k, v in db_config.items():
        db_config[k] = type(v)(os.environ.get(k.upper(), v))
    for k, v in server_config.items():
        server_config[k] = type(v)(os.environ.get(k.upper(), v))
    for k, v in fetch_config.items():
        fetch_config[k] = type(v)(os.environ.get(k.upper(), v))
    for k, v in scheduler_config.items():
        scheduler_config[k] = type(v)(os.environ.get(k.upper(), v))


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
    "val_http": "http://httpbin.org",
    "val_https": "https://httpbin.org",
    "val_timeout": 5,
    "recheck_failed_count": 2,
    "min_pool_size": 50,
    "get_region": True,
    "verify": True,
    "fetch_protocol": ["https", "socks4", "socks5"],
}

scheduler_config = {
    "timezone": "Asia/Shanghai",
    "run_fetch_interval": 1,
    "max_fetch_interval": 30,
    "run_recheck_interval": 20,
    "fetch_semaphore": 32,
    "recheck_semaphore": 16,
}

## BPProxyPool

<p align="center">
<a href="https://github.com/jungheil/bpproxypool"><img src="https://img.shields.io/badge/BPProxyPool-green.svg" title="BPProxyPool"></a>
<a href="https://github.com/jungheil"><img src="https://img.shields.io/badge/Author-jungheil-green.svg" title="Author"></a>
<a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" title="LICENSE"></a>
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/Language-python-blue.svg" title="Language"></a>
<a href="https://github.com/jungheil/bpproxypool/actions/workflows/test_code.yml"><img src ='https://img.shields.io/github/actions/workflow/status/jungheil/bpproxypool/test_code.yml?label=Test' title="Test"></a>
<a href="https://github.com/jungheil/bpproxypool/actions/workflows/build_docker_image.yml"><img src ='https://img.shields.io/github/actions/workflow/status/jungheil/bpproxypool/build_docker_image.yml?label=Build' title="Build"></a>
</p>

     ____  ____  ____                      ____             _
    | __ )|  _ \|  _ \ _ __ _____  ___   _|  _ \ ___   ___ | |
    |  _ \| |_) | |_) | '__/ _ \ \/ / | | | |_) / _ \ / _ \| |
    | |_) |  __/|  __/| | | (_) >  <| |_| |  __/ (_) | (_) | |
    |____/|_|   |_|   |_|  \___/_/\_\\__, |_|   \___/ \___/|_|
                                     |___/

白嫖 IP 池，从互联网中免费的代理网站中爬取并验证代理。这是一个协程实现版本。

### Get start

#### docker-compose

```bash
mkdir bp_proxy_pool && cd bp_proxy_pool
wget -N https://raw.githubusercontent.com/jungheil/bpproxypool/main/docker-compose.yml && docker-compose up
```

#### source

```bash
git clone https://github.com/jungheil/bpproxypool.git bp_proxy_pool
cd bp_proxy_pool
pip3 install -r requirements.txt

python3 bpproxypool.py launch
```

### Config

可以通过添加环境变量（参数名全大写）或者修改文件`config.py`配置

- 数据库配置

  | name         | description | remark |
  | ------------ | ----------- | ------ |
  | `db_conn`    | 数据库地址  |        |
  | `table_name` | 数据库表名  |        |

- API 服务配置

  | name   | description  | remark |
  | ------ | ------------ | ------ |
  | `host` | API 监听地址 |        |
  | `port` | API 监听端口 |        |

- 爬虫设置

  | name                   | description      | remark                 |
  | ---------------------- | ---------------- | ---------------------- |
  | `fetchers`             | 代理获取源       | 见`fetcher/fetcher.py` |
  | `val_http`             | http 验证地址    |                        |
  | `val_https`            | https 验证地址   |                        |
  | `val_timeout`          | 验证超时时间     |                        |
  | `recheck_failed_count` | 失败容许次数     |                        |
  | `min_pool_size`        | 代理池最小数量   |                        |
  | `get_region`           | 是否获取代理地区 |                        |
  | `verify`               | 是否验证 ssl     |                        |
  | `fetch_protocol`       | 爬取协议         |                        |

- 调度器配置

  | name                   | description          | remark                                        |
  | ---------------------- | -------------------- | --------------------------------------------- |
  | `timezone`             | 时区                 |                                               |
  | `run_fetch_interval`   | 运行爬虫间隔时间     | 当代理池中代理数量大于`min_pool_size`不会运行 |
  | `max_fetch_interval`   | 强制运行爬虫间隔时间 |                                               |
  | `run_recheck_interval` | 验证代理池间隔时间   |                                               |
  | `fetch_semaphore`      | 爬虫并行数量         |                                               |
  | `recheck_semaphore`    | 验证代理池并行数量   |                                               |

### API

| api     | method | description        | params     | example                  |
| ------- | ------ | ------------------ | ---------- | ------------------------ |
| /       | GET    | api 介绍           | `None`     |                          |
| /get    | GET    | 随机获取一个代理   | `protocol` | `?protocol=http,https`   |
| /pop    | GET    | 获取并删除一个代理 | `protocol` |                          |
| /all    | GET    | 获取所有代理       | `protocol` |                          |
| /count  | GET    | 查看代理数量       | `None`     |                          |
| /delete | GET    | 删除代理           | `addr`     | `addr=192.168.16.1:6666` |

### Custom Fetcher and Validator

- Fetcher

  见`fetcher/fetcher`

- Validator

  见`helper/validator.py`

### Acknowledgment

- <https://github.com/jhao104/proxy_pool>

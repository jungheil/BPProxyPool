import json
import re


class Proxy(object):
    IP_REGEX = re.compile(
        r"^((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.){3}(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])(?::(?:[0-9]|[1-9][0-9]{1,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5]))$"
    )

    def __init__(
        self,
        addr,
        protocol=[],
        fail_count=0,
        region="",
        anonymous="",
        source="",
        check_count=0,
        last_status=False,
        last_time="",
    ):
        assert self._check_addr(addr), "addr error"
        assert isinstance(protocol, list), "protocol error"
        assert isinstance(fail_count, int), "fail_count error"
        assert isinstance(region, str), "region error"
        assert isinstance(anonymous, str), "anonymous error"
        assert isinstance(source, str), "source error"
        assert isinstance(check_count, int), "check_count error"
        assert isinstance(last_status, bool), "last_status error"
        assert isinstance(last_time, str), "last_time error"

        self._addr = addr
        self._protocol = protocol
        self._fail_count = fail_count
        self._region = region
        self._anonymous = anonymous
        self._source = source
        self._check_count = check_count
        self._last_status = last_status
        self._last_time = last_time

    @classmethod
    def _check_addr(cls, addr):
        return True if cls.IP_REGEX.fullmatch(addr) else False

    @classmethod
    def create_from_json(cls, proxy_json):
        _dict = json.loads(proxy_json)
        return cls(
            addr=_dict.get("addr", ""),
            protocol=_dict.get("protocol", []),
            fail_count=_dict.get("fail_count", 0),
            region=_dict.get("region", ""),
            anonymous=_dict.get("anonymous", ""),
            source=_dict.get("source", ""),
            check_count=_dict.get("check_count", 0),
            last_status=_dict.get("last_status", ""),
            last_time=_dict.get("last_time", ""),
        )

    @property
    def addr(self):
        """代理 ip:port"""
        return self._addr

    @property
    def fail_count(self):
        """检测失败次数"""
        return self._fail_count

    @property
    def region(self):
        """地理位置(国家/城市)"""
        return self._region

    @property
    def anonymous(self):
        """匿名"""
        return self._anonymous

    @property
    def source(self):
        """代理来源"""
        return self._source

    @property
    def check_count(self):
        """代理检测次数"""
        return self._check_count

    @property
    def last_status(self):
        """最后一次检测结果  True -> 可用; False -> 不可用"""
        return self._last_status

    @property
    def last_time(self):
        """最后一次检测时间"""
        return self._last_time

    @property
    def protocol(self):
        """支持的协议"""
        return self._protocol

    @property
    def to_dict(self):
        """属性字典"""
        return {
            "addr": self.addr,
            "protocol": self.protocol,
            "fail_count": self.fail_count,
            "region": self.region,
            "anonymous": self.anonymous,
            "source": self.source,
            "check_count": self.check_count,
            "last_status": self.last_status,
            "last_time": self.last_time,
        }

    @property
    def to_json(self):
        """属性json格式"""
        return json.dumps(self.to_dict, ensure_ascii=False)

    @fail_count.setter
    def fail_count(self, value):
        self._fail_count = value

    @check_count.setter
    def check_count(self, value):
        self._check_count = value

    @last_status.setter
    def last_status(self, value):
        self._last_status = value

    @last_time.setter
    def last_time(self, value):
        self._last_time = value

    @protocol.setter
    def protocol(self, value):
        self._protocol = value

    @region.setter
    def region(self, value):
        self._region = value

import platform

from flask import Flask, jsonify, request
from werkzeug.wrappers import Response

from config import server_config
from handler.db_handler import DBHandler
from helper.proxy import Proxy

app = Flask(__name__)
proxy_handler = DBHandler()


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)

        return super(JsonResponse, cls).force_type(response, environ)


app.response_class = JsonResponse

api_list = [
    {"url": "/get", "params": "protocol: 'e.g. http,https'", "desc": "get a proxy"},
    {
        "url": "/pop",
        "params": "protocol: 'e.g. http,https'",
        "desc": "get and delete a proxy",
    },
    {
        "url": "/delete",
        "params": "addr: 'e.g. 192.168.16.1:6666'",
        "desc": "delete an unable proxy",
    },
    {
        "url": "/all",
        "params": "protocol: 'e.g. http,https'",
        "desc": "get all proxy from proxy pool",
    },
    {"url": "/count", "params": "", "desc": "return proxy count"},
]


@app.route("/")
def index():
    return {"url": api_list}


@app.route("/get/")
def get():
    protocol = request.args.get("protocol")
    protocol = protocol.split(",") if protocol else []
    proxy = proxy_handler.get(protocol)
    return proxy.to_dict if proxy else {"code": 1, "src": "no proxy"}


@app.route("/pop/")
def pop():
    protocol = request.args.get("protocol")
    protocol = protocol.split(",") if protocol else []
    proxy = proxy_handler.pop(protocol)
    return proxy.to_dict if proxy else {"code": 1, "src": "no proxy"}


@app.route("/all/")
def get_all():
    protocol = request.args.get("protocol")
    protocol = protocol.split(",") if protocol else []
    proxies = proxy_handler.get_all(protocol)
    return jsonify([_.to_dict for _ in proxies])


@app.route("/delete/")
def delete():
    addr = request.args.get("addr")
    try:
        proxy = Proxy(addr)
    except Exception:
        return {"code": 2, "src": "addr error"}
    status = proxy_handler.delete(proxy)
    if status:
        return {"code": 0, "src": "delete success"}
    else:
        return {"code": 3, "src": "delete failed"}


@app.route("/count/")
def get_count():
    return proxy_handler.get_count()


def runFlask():
    if platform.system() == "Windows":
        app.run(host=server_config["host"], port=server_config["port"])
    else:
        import gunicorn.app.base

        class StandaloneApplication(gunicorn.app.base.BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super(StandaloneApplication, self).__init__()

            def load_config(self):
                _config = dict(
                    [
                        (key, value)
                        for key, value in self.options.items()
                        if key in self.cfg.settings and value is not None
                    ]
                )
                for key, value in _config.items():
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        _options = {
            "bind": f"{server_config['host']}:{server_config['port']}",
            "workers": 4,
            "accesslog": "log/server.log",
        }
        StandaloneApplication(app, _options).run()


if __name__ == "__main__":
    runFlask()

from threading import Thread

import requests

from flask import Flask, Response, request, redirect

LOOPBACK_PORT = 6753
LOOPBACK_ENDPOINT = "/running"


def check_app_running():
    address = "http://127.0.0.1:{}{}".format(LOOPBACK_PORT, LOOPBACK_ENDPOINT)
    try:
        r = requests.get(address, timeout=0.3)
        return r.ok
    except:
        return False


def launch_loopback(signal):
    t = Thread(target=run_flask, args=(signal,))
    t.setDaemon(True)
    t.start()
    return t


def run_flask(signal):
    a = FlaskAppWrapper("wrap")
    a.add_endpoint(endpoint="/running", endpoint_name="running", handler=signal)
    a.run()


class EndpointSignal(object):
    def __init__(self, signal):
        self.signal = signal
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        self.signal.emit()
        return self.response


class FlaskAppWrapper(object):
    app = None

    def __init__(self, name):
        self.app = Flask(name)

    def run(self):
        self.app.run(port=6753)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointSignal(handler))


if __name__ == "__main__":
    run_flask(None)

import websocket
import json
import os
import logging

try:
    import thread
except ImportError:
    import _thread as thread
import time
import base64


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)


def on_message(ws, message):
    logger.info(message)
    try:
        client_ws = websocket.create_connection(os.getenv("WEBSOCKET_CLIENT"))
        client_ws.send(message)
    except Exception as e:
        logger.exception(e)


def on_error(ws, error):
    logger.error(error)


def on_close(ws):
    logger.warning("### closed ###")


def on_open(ws):
    # import pdb; pdb.set_trace()
    def run(*args):
        ws.send(json.dumps({"type": "subscribeblock", "data": {"cryptoCode": "BTC"}}))
        ws.send(
            json.dumps({"type": "subscribetransaction", "data": {"cryptoCode": "*"}})
        )
        # ws.close()
        logger.info("thread terminating...")

    thread.start_new_thread(run, ())


url = f"ws://{os.getenv('NBXPLORER_URL','')}/v1/cryptos/btc/connect"
credentials = os.getenv("NBXPLORER_CREDENTIALS")
tor_proxy = os.getenv("BITCOIN_TOR_PROXY")
proxy_host = None
proxy_port = None
proxy_type = os.getenv("NBX_PROXY_TYPE")
if tor_proxy:
    proxy_host, proxy_port = tor_proxy.strip().split(":")
    proxy_port = int(proxy_port)
headers = {}
if credentials:
    headers = {
        "Authorization": f"Basic {base64.b64encode(credentials.encode('utf-8')).decode('utf-8')}"
    }
ws = websocket.WebSocketApp(
    url,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_open=on_open,
    header=headers,
)
ws.run_forever(
    http_proxy_host=proxy_host, http_proxy_port=proxy_port, proxy_type=proxy_type,
)


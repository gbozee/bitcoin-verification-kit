import json
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, WebSocketRoute
from starlette.requests import Request
from starlette.config import Config
import service

config = Config(".env")
DEBUG = config("DEBUG", cast=bool, default=False)
BITCOIN_NODE_URL = config("BITCOIN_NODE_URL")
BITCOIN_NODE_USERNAME = config("BITCOIN_NODE_USERNAME")
BITCOIN_NODE_PASSWORD = config("BITCOIN_NODE_PASSWORD")
BITCOIN_TOR_PROXY = config("BITCOIN_TOR_PROXY")
NBXPLORER_URL = config("NBXPLORER_URL", default="")
NBXPLORER_CREDENTIALS = config("NBXPLORER_CREDENTIALS", default="")
CHANNEL_URL = config("CHANNEL_URL", default="memory://")

client = service.BitcoinHelper(
    BITCOIN_NODE_USERNAME,
    BITCOIN_NODE_PASSWORD,
    node_url=BITCOIN_NODE_URL,
    tor_proxy=BITCOIN_TOR_PROXY,
    nbxplorer_url=NBXPLORER_URL,
    nbxplorer_user=NBXPLORER_CREDENTIALS,
)


async def bitcoin_api(request: Request):
    data = await request.json()
    result, status_code = await client.async_api_call(data)
    return JSONResponse(result, status_code=status_code)


app = Starlette(
    debug=DEBUG,
    routes=[
        Route("/", bitcoin_api, methods=["POST"]),
    ],
)


import json
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, WebSocketRoute
from starlette.concurrency import run_until_first_complete
from starlette.requests import Request
from starlette.config import Config
from broadcaster import Broadcast
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

broadcast = Broadcast(CHANNEL_URL)


async def nbxplorer_ws(websocket):
    await websocket.accept()
    await run_until_first_complete(
        (nbxplorer_ws_receiver, {"websocket": websocket}),
        (new_blocks_ws_sender, {"websocket": websocket}),
        (new_transactions_ws_sender, {"websocket": websocket}),
    )


async def nbxplorer_ws_receiver(websocket):
    async for message in websocket.iter_text():
        data = json.loads(message)
        print(data)
        _type = data.get("type") or ""
        if _type == "newblock":
            await broadcast.publish(
                channel="new-blocks", message=json.dumps(data["data"]),
            )
        else:
            await broadcast.publish(
                channel="transactions", message=json.dumps(data["data"])
            )


async def new_blocks_ws_sender(websocket):
    async with broadcast.subscribe(channel="new-blocks") as subscriber:

        async for event in subscriber:
            await websocket.send_text(event.message)


async def new_transactions_ws_sender(websocket):
    async with broadcast.subscribe(channel="transactions") as subscriber:
        async for event in subscriber:
            await websocket.send_text(event.message)


async def bitcoin_api(request: Request):
    data = await request.json()
    result, status_code = await client.async_api_call(data)
    return JSONResponse(result, status_code=status_code)


app = Starlette(
    debug=DEBUG,
    routes=[
        Route("/", bitcoin_api, methods=["POST"]),
        WebSocketRoute("/ws", nbxplorer_ws, name="nbxplorer_ws"),
    ],
    on_startup=[broadcast.connect],
    on_shutdown=[broadcast.disconnect],
)


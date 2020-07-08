import asyncio
import requests
import typing

XPUB_CONVERTER_URL = "https://xpub-converter.vercel.app/api/change-version"


async def loop_helper(callback):
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, callback)
    return await future


class BitcoinHelper:
    def __init__(
        self,
        username,
        password,
        node_url=None,
        tor_proxy=None,
        nbxplorer_url=None,
        nbxplorer_user=None,
    ):
        self.username = username
        self.password = password
        self.node_url = node_url
        self.tor_proxy = tor_proxy
        self.nbxplorer_url = nbxplorer_url
        self.nbxplorer_user = nbxplorer_user
        self.nbxplorer = NBXplorerAPI(f"http://{nbxplorer_url}", self.nbxplorer_session)

    @property
    def request_session(self) -> requests.Session:
        session = requests.session()
        session.auth = (self.username, self.password)
        session.headers.update({"content-type": "application/json"})
        if self.tor_proxy:
            session.proxies = {
                "http": f"socks5h://{self.tor_proxy}",
                "https": f"socks5h://{self.tor_proxy}",
            }
        return session

    @property
    def nbxplorer_session(self) -> requests.Session:
        session = requests.session()
        session.headers.update({"content-type": "application/json"})
        if self.nbxplorer_user:
            session.auth = tuple(self.nbxplorer_user.split(":"))
        if self.tor_proxy:
            session.proxies = {
                "http": f"socks5h://{self.tor_proxy}",
                "https": f"socks5h://{self.tor_proxy}",
            }
        return session

    def nbx_call(self) -> typing.Tuple[typing.Any, int]:
        # payload = {**data}
        return self.nbxplorer.get_current_balance(
            "xpub6CpqPL47XVhmwQcB9m6uxKsZ3s5RTQT6jp2sh8VeyzFyd4iDsNvvf53aPy2MaEgwpEFKGENeckg3SXZfSTEZ2mSqPCAs3B2Ueweww"
        )
        # response = self.nbxplorer_session.get(
        #     # f"http://{self.nbxplorer_url}" + "/v1/cryptos/btc/fees/3",
        #     f"http://{self.nbxplorer_url}"
        #     + "/v1/cryptos/btc/derivations/xpub6CpqPL47XVhmwQcB9m6uxKsZ3s5aewaeadadeaedaweda/balance",
        #     # json=payload
        # )
        # return response.json(), response.status_code

    def api_call(self, data) -> typing.Tuple[typing.Any, int]:
        payload = {"jsonrpc": "1.0", "id": "curltest", **data}
        response = self.request_session.post(self.node_url, json=payload)
        return response.json(), response.status_code

    def convert_public_key(self, xpub, target="xpub"):
        response = requests.get(
            XPUB_CONVERTER_URL, params={"xpub": xpub, "target": target}
        )
        if response.status_code == 200:
            return response.json()["result"]
        raise ValueError(f"Could not convert public key to {target}")

    async def async_api_call(self, data):
        return await loop_helper(lambda: self.api_call(data))


class NBXplorerAPI:
    def __init__(self, base_url, session: requests.Session):
        self.base_url = base_url
        self.session = session

    def build_url(self, path, crypto="btc"):
        return f"{self.base_url}/v1/cryptos/{crypto}{path}"

    def post(self, path, **kwargs) -> requests.Response:
        url = self.build_url(path)
        return self.session.post(url, **kwargs)

    def get(self, path, **kwargs) -> requests.Response:
        url = self.build_url(path)
        return self.session.get(url, **kwargs)

    def track_public_key_or_address(self, public_key, **kwargs):
        path = self.get_path(public_key, **kwargs)
        response = self.post(f"/{path}/{public_key}")
        return response.text

    def get_path(self, public_key_or_address, target="xpub"):
        if public_key_or_address.startswith(target):
            return "derivations"
        return "addresses"

    def get_transactions(
        self, public_key_or_address: str = "", transaction_id: str = "", **kwargs
    ):
        url = "/transactions"
        if public_key_or_address:
            path = self.get_path(public_key_or_address, **kwargs)
            url = f"/{path}/{public_key_or_address}{url}"
        if transaction_id:
            url += f"/{transaction_id}"
        response = self.get(url)
        return response.json()

    def get_current_balance(self, public_key, **kwargs):
        path = self.get_path(public_key, **kwargs)
        response = self.get(f"/{path}/{public_key}/balance")
        return response.json()

    def get_address(self, public_key, **kwargs):
        path = self.get_path(public_key, **kwargs)
        url = f"/{path}/{public_key}/addresses/unused"
        response = self.get(url)
        return response.json()

    def get_websocket(self,):
        response = self.get("/connect")
        import pdb; pdb.set_trace()
        return response.text

    def node_rpc_proxy(self, data):
        payload = {"jsonrpc": "1.0", "id": "curltest", **data}
        response = self.post(
            "/rpc", headers={"content-type": "application/json"}, json=payload
        )
        return response.json(), response.status_code

    async def async_call(self, name, *args, **kwargs):
        func = getattr(self, name)
        return await loop_helper(lambda: func(*args, **kwargs))


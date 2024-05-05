import re
import asyncio
from datetime import datetime
from typing import Awaitable

import requests
from aiolimiter import AsyncLimiter
from aiohttp import ClientResponse, ClientSession, BasicAuth, ClientProxyConnectionError


PROXY_RX = re.compile(r"(https?://)?(\d{1,3}\.){3}\d{1,3}:\d{2,5}@[\d\w]+:[\d\w]+")

MAX_TRIES = 3


class WrongProxyStructure(Exception):
    pass


class NotWorkingProxy(Exception):
    pass


class BaseScraper:
    """
    max_rate: maximum requests per rate_period
    rate_period: period in seconds (default 1 second)
    """

    BASE_HEADERS = {}

    def __init__(
        self,
        api_key: str = None,
        proxy: str = None,
        max_rate: int = 49,
        rate_period: float = 1,
        debug: bool = False,
    ) -> None:
        self.rate_limit = AsyncLimiter(max_rate, rate_period)
        self._headers = self._get_headers(api_key)

        self._debug = debug

        self._proxy_url = None
        self._proxy_auth = None
        if proxy:
            proxy_url, proxy_username, proxy_password = self._get_proxy_data(
                proxy,
            )

            self._check_proxy(proxy_url, proxy_username, proxy_password)

            self._proxy_url = proxy_url
            self._proxy_auth = BasicAuth(
                login=proxy_username,
                password=proxy_password,
            )

    def _get_headers(
        self,
        api_key: str,
    ) -> dict:
        headers = self.BASE_HEADERS
        if api_key:
            self.add_api_header(headers, api_key)

        return headers

    def _get_proxy_data(self, proxy: str) -> tuple[str, BasicAuth]:
        self._check_proxy_structure(proxy)

        proxy_url = re.findall(r"([0-9a-z:.]+)@", proxy, re.IGNORECASE)[0]
        proxy_url = "http://" + proxy_url
        proxy_username = re.findall(r"@([0-9a-z]+):", proxy, re.IGNORECASE)[0]
        proxy_password = re.findall(r":([0-9a-z]+)$", proxy, re.IGNORECASE)[0]

        return proxy_url, proxy_username, proxy_password

    def _check_proxy_structure(self, proxy: str) -> None:
        """Should be like '154.195.18.33:63004@GFNau6gw:9J9siqgu' this"""
        matched = PROXY_RX.match(proxy)
        if not matched:
            raise WrongProxyStructure(
                "Should be like '154.195.18.33:63004@GFNau6gw:9J9siqgu' this"
            )

    def _check_proxy(
        self,
        proxy_url: str,
        proxy_username: str,
        proxy_password: str,
    ) -> bool:
        URL = "https://example.com/"
        proxies = {
            "http": f"{proxy_url}@{proxy_username}:{proxy_password}",
        }

        data = requests.get(
            URL,
            proxies=proxies,
            timeout=15,
        ).text

        if "Example" not in data:
            raise NotWorkingProxy("Proxy may have expired")

    def _request_limiter(coro: Awaitable):
        async def wrapper(self, *args, **kwargs):
            rate_limit: AsyncLimiter = self.rate_limit
            async with rate_limit:
                output = await coro(self, *args, **kwargs)
                return output

        return wrapper

    def add_api_header(self, headers: dict, api_key: str) -> None:
        """Add auth header"""

        headers.update({"Authorization": f"Bearer {api_key}"})

    async def extractor(self, response: ClientResponse):
        data = await response.text()
        return data

    @_request_limiter
    async def request(self, url: str):
        if self._debug:
            print(datetime.now().strftime("%H-%M-%S"), url)

        tries = 3
        while tries:
            try:
                tries -= 1
                async with ClientSession() as session:
                    async with session.request(
                        method="get",
                        url=url,
                        proxy=self._proxy_url,
                        proxy_auth=self._proxy_auth,
                        headers=self._headers,
                    ) as response:
                        return await self.extractor(response)

            except ClientProxyConnectionError as ex:
                print(ex)


async def test():
    scraper = BaseScraper()

    d = await scraper.request("https://example.com/")
    print(d)


if __name__ == "__main__":
    asyncio.run(test())

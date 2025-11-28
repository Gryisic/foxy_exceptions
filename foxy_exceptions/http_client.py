from typing import Optional, Dict

import aiohttp
import requests


class AsyncHTTPClient:
    def __init__(self, timeout: float = 5.0, headers: Optional[Dict[str, str]] = None):
        self.timeout = timeout
        self.headers = headers or {}

    async def post_json(self, url: str, payload: dict) -> bool:
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        async with aiohttp.ClientSession(timeout=timeout, headers=self.headers) as session:
            async with session.post(url, json=payload) as resp:
                return 200 <= resp.status < 300

class SyncHTTPClient:
    def __init__(self, timeout: float = 5.0, headers: Optional[Dict[str, str]] = None):
        self.timeout = timeout
        self.headers = headers or {}

    def post_json(self, url: str, payload: dict) -> bool:
        try:
            r = requests.post(url, json=payload, headers=self.headers, timeout=self.timeout)
            return 200 <= r.status_code < 300
        except requests.RequestException:
            return False


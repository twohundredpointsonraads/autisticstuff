import asyncio

import aiohttp

from .core import retry_with_backoff


class RetryableClientSession:
	def __init__(
		self,
		max_retries: int,
		timeout: int,
		**session_kwargs,
	):
		self.max_retries = max_retries
		self.timeout = aiohttp.ClientTimeout(total=timeout)
		self.session_kwargs = session_kwargs
		self._session = None

	async def __aenter__(self):
		self._session = aiohttp.ClientSession(timeout=self.timeout, **self.session_kwargs)
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		if self._session:
			await self._session.close()

	async def _request_with_retry(self, method: str, url: str, **kwargs):
		async def _make_request():
			return await self._session.request(method, url, **kwargs)

		return await retry_with_backoff(
			_make_request,
			max_retries=self.max_retries,
			exceptions=(
				aiohttp.ClientError,
				asyncio.TimeoutError,
				aiohttp.ServerDisconnectedError,
				aiohttp.ClientConnectorError,
			),
		)

	async def get(self, url: str, **kwargs):
		return await self._request_with_retry("GET", url, **kwargs)

	async def post(self, url: str, **kwargs):
		return await self._request_with_retry("POST", url, **kwargs)

	async def put(self, url: str, **kwargs):
		return await self._request_with_retry("PUT", url, **kwargs)

	async def delete(self, url: str, **kwargs):
		return await self._request_with_retry("DELETE", url, **kwargs)

	async def patch(self, url: str, **kwargs):
		return await self._request_with_retry("PATCH", url, **kwargs)

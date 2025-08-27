import asyncio
from collections.abc import Callable
from typing import Any

from autisticstuff.logs import get_logger


_logger = get_logger("aiohttp.retry_with_backoff")


async def retry_with_backoff(
	func: Callable,
	*args,
	max_retries: int,
	delay: float,
	backoff_factor: float = 2.0,
	exceptions: tuple = (Exception,),
	**kwargs,
) -> Any:
	for attempt in range(max_retries + 1):
		try:
			return await func(*args, **kwargs)
		except exceptions as e:
			if attempt == max_retries:
				_logger.error(f"failed after {max_retries} retries: {e}")
				raise

			wait_time = delay * (backoff_factor**attempt)
			_logger.warning(f"attempt {attempt + 1} failed: {e}; retrying in {wait_time:.2f}s")
			await asyncio.sleep(wait_time)

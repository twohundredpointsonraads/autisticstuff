from collections.abc import Callable
from functools import lru_cache
from typing import Any


def add_cached_handler_for_instance(instance: type[Callable[[], object]], *args: object, **kwargs: object) -> Callable[[], Any]:
	@lru_cache
	def _():
		return instance(*args, **kwargs)

	return _
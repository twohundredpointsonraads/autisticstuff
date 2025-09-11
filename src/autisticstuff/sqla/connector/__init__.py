from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Session, sessionmaker

from ...logs import get_logger


class SQLDB:
	_sync_engine = _async_engine = _sync_session_factory = _async_session_factory = None

	logger = get_logger("sqldb.instance")

	def __init__(self, async_uri: str, sync_uri: str, echo: bool = False, pool_size: int = 10) -> None:
		self.__async_uri = async_uri
		self.__sync_uri = sync_uri
		self.echo = echo
		self.pool_size = pool_size

	def __enter__(self):
		return self

	async def __aenter__(self):
		return self

	async def __aexit__(self, *args):
		if self._sync_engine:
			self._sync_engine.dispose()
			self.logger.info(" -> (__aexit__) closed sync db connection")
		if self._async_engine:
			await self._async_engine.dispose()
			self.logger.info(" -> (__aexit__) closed async db connection")

	def __async_init(self):
		self._async_engine = create_async_engine(
			url=self.__async_uri,
			echo=self.echo,
			pool_size=self.pool_size,
		)
		self._async_session_factory = async_sessionmaker(bind=self._async_engine, expire_on_commit=False)
		self.logger.debug(  # noqa: PLE1205
			" -> (__async_init) successfully initialized async db connection, engine.status = {} sessionmaker.status = {}",
			self._async_engine.name is not None,
			self._async_session_factory is not None,
		)

	@property
	def asyncmaker(self) -> async_sessionmaker[AsyncSession]:
		if self._async_engine is None or self._async_session_factory is None:
			self.logger.debug(" -> (asyncmaker) async_sf not found, initializing")
			self.__async_init()
			if self._async_engine is None or self._async_session_factory is None:
				self.logger.error(c := " -> (asyncmaker) could not asynchronously connect to pgsql")
				raise TimeoutError
		self.logger.debug(" -> success getting (asyncmaker)")
		return self._async_session_factory

	def __sync_init(self):
		self._sync_engine = create_engine(
			url=self.__sync_uri,
			echo=self.echo,
			pool_size=self.pool_size,
		)
		self._sync_session_factory = sessionmaker(bind=self._sync_engine, expire_on_commit=False)
		self.logger.debug(  # noqa
			" -> (__sync_init) successfully initialized sync db connection,\n"
			"\t\t\t\tengine.status = {} sessionmaker.status = {}",
			self._sync_engine.name is not None,
			self._sync_session_factory is not None,
		)

	@property
	def syncmaker(self) -> sessionmaker[Session]:
		if self._sync_engine is None or self._sync_session_factory is None:
			self.logger.debug(" -> (syncmaker) not found, initializing...")
			self.__sync_init()
			if self._sync_engine is None or self._sync_session_factory is None:
				self.logger.error(c := " -> (syncmaker) could not synchronously connect to pgsql")
				raise Exception(detail=c)
		self.logger.debug(" -> success getting (syncmaker)")
		return self._sync_session_factory

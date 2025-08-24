from __future__ import annotations

import logging
import re
from collections.abc import Callable
from os import PathLike, getenv
from types import UnionType, NoneType

import loguru
from dotenv import load_dotenv
from dataclasses import dataclass, Field
from typing import Any

__all__ = ["AppSettings", "SettingsField"]

@dataclass(init=True, slots=True, frozen=True)
class SettingsField[T]:
	default: T = None
	factory: Callable[[], T] | str = None
	nullable: bool = True


@dataclass
class AppSettings:
	__ALLOWED_TYPES: frozenset[type] = frozenset((int, float, complex, str, bool, NoneType))

	@staticmethod
	def _evaluate_var(_type: type, _var: str) -> Any:
		if _type is bool:
			return "true" in _var.lower()
		return _type(_var)

	def __init__(self, dotenv_path: str | PathLike[str] | None = None, logger: logging.Logger | loguru.Logger | None = None, explicit_format: bool = True) -> None:
		"""
		Initialize AppSettings object

		Args:
			dotenv_path (str | PathLike[str] | None) = None: when None, search recursively for .env
			logger (logging.Logger | loguru.Logger | None) = None: when None, defaults to loguru.Logger
			explicit_format (bool) = True: if True, all variables should be named with only capital letters and underscores
		"""
		load_dotenv(dotenv_path=dotenv_path)
		self._logger: loguru.Logger = loguru.logger if logger is None else logger
		_settings_fields: dict[str, SettingsField] = {}
		for _attribute in self.__annotations__:
			_settings_fields[_attribute] = self.__class__.__dict__[_attribute]
		_attribute_map: list[tuple[str, str]] = []
		_annotations: dict[str, type] = self.__annotations__
		print(_annotations, _settings_fields)
		for _attribute in _settings_fields:
			if explicit_format and not re.match(r"[A-Z_]", _attribute):
				raise AttributeError("AppSettings attributes should contain only capital letters and underscores")

			_settings_field = _settings_fields[_attribute]
			_annotated_type = _annotations[_attribute]
			if _annotated_type not in self.__ALLOWED_TYPES and isinstance(_annotated_type, UnionType) and not all(_type in self.__ALLOWED_TYPES for _type in _annotated_type.__args__):
				raise TypeError(f"{_annotated_type} is not allowed for annotations as it is mutable")
			_string_value: str | None = getenv(_attribute, None)

			if _string_value is None:
				if _settings_field.default is not None:
					self._logger.info(f"Successfully evaluated {_attribute}={_settings_field.default} by default")
					setattr(self, _attribute, _settings_field.default)
					continue
				if _settings_field.factory is not None and isinstance(_settings_field.factory, str):
					self._logger.info(f"Postponed {_attribute} initialization as factory is a property")
					_attribute_map.append((_attribute, _settings_field.factory))
					continue
				if callable(_settings_field.factory):
					self._logger.info(f"Successfully evaluated {_attribute} from factory")
					setattr(self, _attribute, _settings_field.factory())
					continue
				if _settings_field.nullable:
					self._logger.info(f"Nulled {_attribute}")
					setattr(self, _attribute, None)
					continue
				raise ValueError(f"Required field {_attribute} was not found in .env")

			_value: _annotated_type = self._evaluate_var(_annotated_type, _string_value)
			self._logger.info(f"Successfully evaluated {_attribute}={_value}")
			setattr(self, _attribute, _value)

		self.__init_factory_defined(_attribute_map=_attribute_map)


	def __init_factory_defined(self, _attribute_map: list[tuple[str, str]]):
		for (_attribute, _property) in _attribute_map:
			if _property not in self.__class__.__dict__:
				raise AttributeError(f"Property {_property} was not found in {self.__class__.__name__}")
			if not isinstance(getattr(self.__class__, _property), property):
				raise TypeError(f"Method {_property} is not a property")
			self._logger.info(f"Successfully evaluated {_attribute} from property {_property}")
			setattr(self, _attribute, getattr(self, _property))

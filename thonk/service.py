from abc import ABCMeta, abstractmethod
from typing import List, Iterator
from itertools import chain

__all__ = ["Service", "Provider", "ProviderAggregator"]

class Service:
	def __init__(self, name: str, dst_host: str, port: int, protocol: str = "tcp"):
		self.name = name
		self.host = dst_host
		self.port = port
		self.protocol = protocol

	@property
	def port_range(self):
		return str(self.port)  # TODO: Port range support

class Provider(metaclass=ABCMeta):
	@abstractmethod
	def update(self):
		pass
	
	@abstractmethod
	def get_active_rules(self) -> List[Service]:
		pass

class ProviderAggregator(Provider):
	def __init__(self, *providers):
		self.providers = list(providers)

	def add_provider(self, provider):
		self.providers.append(provider)

	def update(self):
		for p in self.providers:
			p.update()

	def get_active_rules(self) -> Iterator:
		return chain.from_iterable(
			map(lambda p: p.get_active_rules(), self.providers)
		)

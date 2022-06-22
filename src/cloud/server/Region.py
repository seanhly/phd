from typing import List, Type
from cloud.Vendor import Vendor

from cloud.server.Entity import Entity


class Region(Entity):
	id: str
	city: str
	country: str
	continent: str
	options: List[str]

	def __init__(self, data, vendor: Type[Vendor] = None):
		self.__dict__ = data
		self.vendor = vendor

	def __str__(self) -> str:
		return f"{self.city}, {self.country}"

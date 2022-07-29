from typing import Type
from cloud.Vendor import Vendor
from cloud.server.Entity import Entity


class OperatingSystem(Entity):
	id: int
	name: str
	arch: str
	family: str

	def __init__(self, data, vendor: Type["Vendor"]):
		self.__dict__ = data
		self.vendor = vendor

	def __str__(self) -> str:
		return f"{self.family} {self.name}"

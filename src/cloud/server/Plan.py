from typing import List, Type
from cloud.Vendor import Vendor
from cloud.server.Entity import Entity


class Plan(Entity):
	id: str
	vcpu_count: int
	ram: int
	disk: int
	disk_count: int
	bandwidth: int
	monthly_cost: int
	type: str
	locations: List[str]

	def __init__(self, data, vendor: Type[Vendor]):
		self.__dict__ = data
		self.vendor = vendor

	def __str__(self) -> str:
		return (
			f"{self.ram} MB RAM, {self.vcpu_count} CPU,"
			f"{self.disk_count} x {self.disk} GB DISK,"
			f"€{self.monthly_cost} {self.type}"
		)

from typing import List, Type
from cloud.Vendor import Vendor
from cloud.server.Entity import Entity
from cloud.server.Instance import Instance
from JSON import JSON
from os.path import exists

from constants import PHD_POOL


class Pool(Entity):
	pool: List[Instance]

	def __init__(self, data, vendor: Type[Vendor]):
		self.__dict__ = data
		self.vendor = vendor

	@staticmethod
	def load(vendor: Type[Vendor]):
		pool = None
		if exists(PHD_POOL):
			with open(PHD_POOL, "r") as f:
				pool = [Instance(i, vendor) for i in JSON.load(f)]
		if not pool:
			pool = vendor.list_instances(label="phd")
			with open(PHD_POOL, "w") as f:
				JSON.dump([
					dict([(k, v) for k, v in i.__dict__.items() if k != "vendor"])
					for i in pool
				], f)
		return Pool(dict(pool=pool), vendor)
	
	def dump(self):
		with open(PHD_POOL, "w") as f:
			JSON.dump([
				dict([(k, v) for k, v in i.__dict__.items() if k != "vendor"])
				for i in self.pool
			], f)
	
	def remove(self, id: str):
		removed = False
		i = 0
		while i < len(self.pool):
			instance = self.pool[i]
			if instance.id == id:
				del self.pool[i]
				removed = True
			i += 1
		return removed

	def add_all(self, instances: List[Instance]):
		self.pool += instances

	def update(self, instances: List[Instance]):
		self.pool = instances
		self.dump()

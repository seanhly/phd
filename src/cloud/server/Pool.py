from cProfile import label
from typing import List, Tuple, Type
from cloud.Vendor import Vendor
from cloud.server.Entity import Entity
from cloud.server.Instance import Instance
from JSON import JSON
from os.path import exists
from datetime import datetime

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
			print(str(instance))
			if instance.id == id:
				del self.pool[i]
				removed = True
			i += 1
		return removed

	def add(self, instance: Instance):
		for i in range(len(self.pool)):
			if self.pool[i].id == id:
				return False
		self.pool.append(instance)
		return True

	def update(self, instances: List[Instance]):
		self.pool = instances
		self.dump()

	def install(self):
		for instance in self.pool:
			instance.install()
	
	def run_grobid(self):
		for instance in self.pool:
			instance.run_grobid()
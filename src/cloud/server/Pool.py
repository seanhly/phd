from cProfile import label
from typing import List, Tuple, Type
from cloud.Vendor import Vendor
from cloud.server.Entity import Entity
from cloud.server.Instance import Instance
from JSON import JSON
from os.path import exists

from constants import PHD_POOL


class Pool(Entity):
	pool: List[
		Tuple[int, bool, Instance]
	]

	def __init__(self, data, vendor: Type[Vendor]):
		self.__dict__ = data
		self.vendor = vendor

	@staticmethod
	def load(vendor: Type[Vendor]):
		pool = None
		if exists(PHD_POOL):
			with open(PHD_POOL, "r") as f:
				pool = [[a, b, Instance(c, vendor)] for a, b, c in JSON.load(f)]
		if not pool:
			pool = [
				[0, False, instance]
				for instance in vendor.list_instances(label="phd")
			]
			with open(PHD_POOL, "w") as f:
				JSON.dump([
					[a, b, dict([(k, v) for k, v in c.__dict__.items() if k != "vendor"])]
					for a, b, c in pool
				], f)
		if not pool:
			vendor.create_instance()
			pool = [
				[0, False, instance]
				for instance in vendor.list_instances(label="phd")
			]
		if pool:
			return Pool(dict(pool=pool), vendor)
	
	def run_grobid(self):
		for created_ts, processing, instance in self.pool:
			instance.run_grobid()
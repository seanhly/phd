from abc import ABC, abstractclassmethod
from typing import List, Optional

from cloud.server.Instance import Instance


class Vendor(ABC):
	@abstractclassmethod
	def list_plans(cls):
		pass

	@abstractclassmethod
	def list_regions(cls):
		pass

	@abstractclassmethod
	def list_operating_systems(cls):
		pass

	@abstractclassmethod
	def list_ssh_keys(cls):
		pass

	@abstractclassmethod
	def list_instances(cls, label: Optional[str] = None) -> List[Instance]:
		pass

	@abstractclassmethod
	def create_instance(cls, region, plan, os, sshkey):
		pass

	@abstractclassmethod
	def destroy_instance(cls, id: str):
		pass
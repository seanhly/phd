from typing import Type
from cloud.Vendor import Vendor
from cloud.server.Entity import Entity


class SSHKey(Entity):
	id: str
	date_created: int
	name: str
	ssh_key: str

	def __init__(self, data, vendor: Type[Vendor]):
		self.__dict__ = data
		import dateparser
		self.date_created = int(
			dateparser.parse(str(self.date_created)).timestamp())
		self.vendor = vendor

	def __str__(self):
		return f"{self.id}\t{self.name}\t{self.ssh_key}\t{self.date_created}"

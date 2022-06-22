from typing import Type
import dateparser
from cloud.Vendor import Vendor

from cloud.server.Entity import Entity

class SSHKey(Entity):
	id: str
	date_created: int
	name: str
	ssh_key: str

	def __init__(self, data, vendor: Type[Vendor]):
		self.__dict__ = data
		self.date_created = int(dateparser.parse(self.date_created).timestamp())
		self.vendor = vendor
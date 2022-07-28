from typing import List
from cloud.server.Entity import Entity


class Instance(Entity):
	id: str
	os: str
	ram: int
	disk: int
	main_ip: str
	vcpu_count: int
	region: str
	plan: str
	date_created: int
	status: str
	allowed_bandwidth: int
	netmask_v4: str
	gateway_v4: str
	power_status: str
	server_status: str
	v6_network: str
	v6_main_ip: str
	v6_network_size: str
	label: str
	internal_ip: str
	kvm: str
	hostname: str
	tag: str
	tags: List[str]
	os_id: int
	app_id: int
	image_id: str
	firewall_group_id: str
	features: List[str]

	def __init__(self, data, vendor):
		self.__dict__ = data
		import dateparser
		if "date_created" in data and type(data["date_created"]) != int:
			self.date_created = int(
				dateparser.parse(data["date_created"]).timestamp()
			)
		self.vendor = vendor

	def __str__(self):
		d = self.__dict__
		if "main_ip" in d:
			s = f"{self.id}\t{self.main_ip} ({self.ram}, {self.status}, {self.server_status}, {self.internal_ip}, {self.v6_main_ip})"
		else:
			s = str(d)
		
		return s

	def destroy(self):
		self.vendor.destroy_instance(self.id)
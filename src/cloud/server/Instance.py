import subprocess
from typing import List
import dateparser
from cloud.server.Entity import Entity
from constants import EXECUTABLE, INSTALL_SCRIPT_URL

INSTALL_SCRIPT = f"sh -c \"$(curl -fsSL {INSTALL_SCRIPT_URL})\""


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
		if "date_created" in data and type(data["date_created"]) != int:
			self.date_created = int(
				dateparser.parse(data["date_created"]).timestamp()
			)
		self.vendor = vendor

	def __str__(self):
		return str(self.__dict__)

	def destroy(self):
		self.vendor.destroy_instance(self.id)

	def install(self):
		install = subprocess.Popen(
			[
				"/usr/bin/ssh",
				f"root@{self.main_ip}",
				INSTALL_SCRIPT
			]
		)
		install.wait()
	
	def run_grobid(self):
		remote = subprocess.Popen(
			[
				"/usr/bin/ssh",
				f"root@{self.main_ip}",
				f"INSTALL_SCRIPT && {EXECUTABLE} local-grobid",
			]
		)
		remote.wait()
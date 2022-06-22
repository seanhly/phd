import subprocess
from typing import List
import dateparser
from cloud.server.Entity import Entity
from constants import GROBID_DIR_PATH, GROBID_EXEC_PATH, GROBID_GIT_SOURCE, INSTALL_SCRIPT_URL
from os.path import exists
from os import makedirs


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

	def run_grobid(self):
		cmd = subprocess.Popen(
			[
				"/usr/bin/ssh",
				f"root@{self.main_ip}",
				f"sh -c \"$(curl -fsSL {INSTALL_SCRIPT_URL})\"",
			],
			cwd=GROBID_DIR_PATH,
		)
		cmd.wait()
		return
		pipeline = []
		if not exists(GROBID_DIR_PATH):
			makedirs(GROBID_DIR_PATH)
		if not exists(GROBID_EXEC_PATH):
			pipeline.append(f"git clone {GROBID_GIT_SOURCE} .")
		pipeline.append(f"{GROBID_EXEC_PATH} run")
		tmux = subprocess.Popen(
			[
				"/usr/bin/tmux",
				"new-session",
				"-s",
				"phd",
				" && ".join(pipeline)
			],
			cwd=GROBID_DIR_PATH,
		)
		tmux.wait()
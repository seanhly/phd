import subprocess
from typing import List
import dateparser
from cloud.server.Entity import Entity
from cloud.vendors.Vultr import Vultr
from constants import EXECUTABLE, INSTALL_SCRIPT_URL
import random
from redis import Redis

INSTALL_SCRIPT = f"sh -c \"$(wget {INSTALL_SCRIPT_URL} -O -)\""
POSITION_KEYS = {
	-2: "L2",
	-1: "L",
	+1: "R",
	+2: "R2",
}

def set_connection(host: str, position: int, connection: str):
	Redis(host=host).set(POSITION_KEYS[position], connection)

def get_connection(host: str, position: int):
	return Redis(host=host).get(POSITION_KEYS[position])

def set_neighbours(a: str, position: int, b: str):
	set_connection(a, position, b)
	set_connection(b, -position, a)


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
		d = self.__dict__
		if "main_ip" in d:
			s = f"{self.id}\t{self.main_ip} ({self.ram}, {self.status}, {self.server_status}, {self.internal_ip}, {self.v6_main_ip})"
		else:
			s = str(d)
		
		return s

	def destroy(self):
		self.vendor.destroy_instance(self.id)
	
	def set_connection(self, position: int, connection: str):
		set_connection(self.main_ip, position, connection)

	def set_neighbours(self, position: int, neighbour: str):
		set_neighbours(self.main_ip, position, neighbour)

	def get_connection(self, position: int):
		return get_connection(self.main_ip, position)
	
	def allow_communication(self, hosts: List[str]):
		print(f"Allowing communication between {self.main_ip} and [{', '.join(hosts)}]...")
		threads = [
			subprocess.Popen(
				[
					"/usr/bin/ssh",
					"-o",
					"StrictHostKeyChecking=no",
					f"root@{self.main_ip}",
					" && ".join(
						f"/usr/bin/ufw allow {host}"
						for host in hosts
					)
				]
			)
		]
		for host in hosts:
			threads += [
				subprocess.Popen(
					[
						"/usr/bin/ssh",
						"-o",
						"StrictHostKeyChecking=no",
						f"root@{host}",
						" && ".join(
							f"/usr/bin/ufw allow {host}"
							for h in (*hosts, self.main_ip)
							if h != host
						)
					]
				)
			]
		for thread in threads:
			thread.wait()
		print("Firewall rules added.")
	
	def install(self):
		instances = [
			instance
			for instance in Vultr.list_instances(label="phd")
			if instance.id != self.id
		]
		# General installation of the new worker.
		print(f"Installing worker software on {self.main_ip}.")
		remote = subprocess.Popen(
			[
				"/usr/bin/ssh",
				"-o",
				"StrictHostKeyChecking=no",
				f"root@{self.main_ip}",
				f"{INSTALL_SCRIPT}",
			]
		)
		remote.wait()
		if len(instances) == 1:
			instance = instances[0]
			self.allow_communication([instance.main_ip])
			left = random_instance.left()
			print("Updating neighbourhood connections...")
			self.set_neighbours(1, instance.main_ip)
			instance.set_neighbours(1, self.main_ip)
			self.set_neighbours(2, self.main_ip)
			instance.set_neighbours(2, instance.main_ip)
			print("Neighbourhood updated.")
		elif len(instances) > 1:
			random_instance = random.choice(instances)
			right = random_instance.left()
			two_doors_right: str = random_instance.get_neighbour(+2)
			left = random_instance.left()
			self.allow_communication([random_instance.main_ip, right, two_doors_right, left])
			print("Updating neighbourhood connections...")
			self.set_neighbours(-1, random_instance.main_ip)
			self.set_neighbours(1, right)
			random_instance.set_neighbours(+2, right)
			self.set_neighbours(-2, left)
			self.set_neighbours(+2, two_doors_right)
			print("Neighbourhood updated.")


	def run_grobid(self):
		remote = subprocess.Popen(
			[
				"/usr/bin/ssh",
				"-o",
				"StrictHostKeyChecking=no",
				f"root@{self.main_ip}",
				f"{EXECUTABLE} local-grobid",
			]
		)
		remote.wait()
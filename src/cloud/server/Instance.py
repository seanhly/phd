import subprocess
from typing import List
import dateparser
from cloud.server.Entity import Entity
from constants import EXECUTABLE, INSTALL_SCRIPT_URL
import random
from redis import Redis
from redis.exceptions import TimeoutError

INSTALL_SCRIPT = f"sh -c \"$(wget {INSTALL_SCRIPT_URL} -O -)\""
POSITION_KEYS = {
	-2: "L2",
	-1: "L",
	+1: "R",
	+2: "R2",
}

def redis_connection(host: str):
	Redis(host=host, socket_timeout=2, port=995)

def set_neighbour(host: str, position: int, neighbour: str):
	process = subprocess.Popen(
		[
			"/usr/bin/ssh",
			"-o",
			"StrictHostKeyChecking=no",
			f"root@{host}",
			f"/usr/bin/redis-cli",
		],
		stdin=subprocess.PIPE,
	)
	process.stdin.write(
		bytes(
			f"set {POSITION_KEYS[position]} {neighbour}",
			encoding="utf8"
		)
	)
	process.stdin.close()
	process.wait()

def get_neighbour(host: str, position: int):
	process = subprocess.Popen(
		[
			"/usr/bin/ssh",
			"-o",
			"StrictHostKeyChecking=no",
			f"root@{host}",
			f"/usr/bin/redis-cli",
		],
		stdin=subprocess.PIPE,
	)
	process.stdin.write(
		bytes(
			f"get {POSITION_KEYS[position]}",
			encoding="utf8"
		)
	)
	return process.stdout.read().decode().strip()

def set_neighbours(a: str, position: int, b: str):
	set_neighbour(a, position, b)
	set_neighbour(b, -position, a)


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
	
	def set_neighbour(self, position: int, connection: str):
		set_neighbour(self.main_ip, position, connection)

	def set_neighbours(self, position: int, neighbour: str):
		set_neighbours(self.main_ip, position, neighbour)

	def get_neighbour(self, position: int):
		return get_neighbour(self.main_ip, position)
	
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
						f"/usr/sbin/ufw allow from {host}"
						for host in hosts
					)
				]
			)
		]
		for host in hosts:
			other_hosts = (
				h
				for h in hosts
				if h != host
			)
			threads += [
				subprocess.Popen(
					[
						"/usr/bin/ssh",
						"-o",
						"StrictHostKeyChecking=no",
						f"root@{host}",
						" && ".join(
							f"/usr/sbin/ufw allow from {h}"
							for h in (*other_hosts, self.main_ip)
						)
					]
				)
			]
		for thread in threads:
			thread.wait()
		print("Firewall rules added.")
	
	def install(self):
		from cloud.vendors.Vultr import Vultr
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
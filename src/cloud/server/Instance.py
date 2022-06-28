import subprocess
from typing import List, Set
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

def set_neighbour(a: str, position: int, b: str):
	process = subprocess.Popen(
		[
			"/usr/bin/ssh",
			"-o",
			"StrictHostKeyChecking=no",
			f"root@{a}",
			f"/usr/bin/redis-cli",
		],
		stdin=subprocess.PIPE,
	)
	process.stdin.write(
		bytes(
			f"set {POSITION_KEYS[position]} {b}",
			encoding="utf8"
		)
	)
	process.stdin.close()

	return process

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
		stdout=subprocess.PIPE,
	)
	process.stdin.write(
		bytes(
			f"get {POSITION_KEYS[position]}",
			encoding="utf8"
		)
	)
	return process.stdout.read().decode().strip()

def set_neighbours(a: str, position: int, b: str):
	return [
		set_neighbour(a, position, b),
		set_neighbour(b, -position, a),
	]


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
	
	@classmethod
	def install(cls, new_instances: Set[str]):
		from cloud.vendors.Vultr import Vultr
		previous_instances = [
			instance
			for instance in Vultr.list_instances(label="phd")
			if instance.main_ip not in new_instances
		]
		threads = []
		for instance in previous_instances:
			print(f"Allow access to {instance.main_ip} from new workers.")
			threads.append(
				subprocess.Popen(
					[
						"/usr/bin/ssh",
						"-o",
						"StrictHostKeyChecking=no",
						f"root@{ip}",
						" && ".join(
							f"/usr/sbin/ufw allow from {new_instance}"
							for new_instance in new_instances
						)
					]
				)
			)
		for ip in new_instances:
			# General installation of the new worker.
			print(f"Installing worker software on {ip}.")
			threads.append(
				subprocess.Popen(
					[
						"/usr/bin/ssh",
						"-o",
						"StrictHostKeyChecking=no",
						f"root@{ip}",
						f"{INSTALL_SCRIPT}",
					]
				)
			)
		for thread in threads:
			thread.wait()
		threads = []
		print("Installed worker software.")
		if previous_instances:
			for new_instance in new_instances:
				print(f"Allow access from {new_instance} to new workers.")
				threads.append(
					subprocess.Popen(
						[
							"/usr/bin/ssh",
							"-o",
							"StrictHostKeyChecking=no",
							f"root@{new_instance}",
							" && ".join(
								f"/usr/sbin/ufw allow from {previous_instance.main_ip}"
								for previous_instance in previous_instances
							)
						]
					)
				)
		for instance in new_instances:
			print(f"Allow access to {instance} from other new workers.")
			other_instances = [
				i for i in new_instances
				if i != instance
			]
			threads.append(
				subprocess.Popen(
					[
						"/usr/bin/ssh",
						"-o",
						"StrictHostKeyChecking=no",
						f"root@{instance}",
						" && ".join(
							f"/usr/sbin/ufw allow from {new_instance}"
							for i in other_instances
						)
					]
				)
			)
		for thread in threads:
			thread.wait()
		threads = []
		if len(previous_instances) == 0:
			single_thread_instances = new_instances
			double_thread_instances = single_thread_instances
			loop_single = 1
			loop_double = 2
		elif len(previous_instances) == 1:
			single_thread_instances = [*new_instances, previous_instances[0]]
			double_thread_instances = single_thread_instances
			loop_single = 1
			loop_double = 2
		elif len(previous_instances) == 2:
			single_thread_instances = [
				previous_instances[-1],
				*new_instances,
				previous_instances[0],
			]
			double_thread_instances = single_thread_instances
			loop_single = 0
			loop_double = 2
		elif len(previous_instances) == 3:
			single_thread_instances = [
				previous_instances[-1],
				*new_instances,
				previous_instances[0],
			]
			double_thread_instances = [
				previous_instances[2],
				*new_instances,
				previous_instances[0],
				previous_instances[1],
			]
			loop_single = 0
			loop_double = 1
		elif len(previous_instances) >= 4:
			any_previous_instance = random.choice(previous_instances)
			neighbourhood = [
				get_neighbour(any_previous_instance.main_ip, -1),
				any_previous_instance,
				get_neighbour(any_previous_instance.main_ip, 1),
				get_neighbour(any_previous_instance.main_ip, 2),
			]
			single_thread_instances = [
				neighbourhood[1],
				*new_instances,
				previous_instances[2],
			]
			double_thread_instances = [
				neighbourhood[0],
				neighbourhood[1],
				*new_instances,
				neighbourhood[2],
				neighbourhood[3],
			]
			loop_single = 0
			loop_double = 0
		threads: List[subprocess.Popen] = []
		for i in range(1 - loop_single, len(single_thread_instances)):
			threads += set_neighbours(
				single_thread_instances[i - 1],
				-1,
				single_thread_instances[i]
			)
		for i in range(2 - loop_double, len(double_thread_instances)):
			threads += set_neighbours(
				double_thread_instances[(i - 2) % len(double_thread_instances)],
				-2,
				double_thread_instances[i]
			)
		for thread in threads:
			thread.wait()	


	@classmethod
	def run_grobid(cls, instances: Set[str]):
		for thread in (
			subprocess.Popen(
				[
					"/usr/bin/ssh",
					"-o",
					"StrictHostKeyChecking=no",
					f"root@{instance}",
					f"{EXECUTABLE} local-grobid",
				]
			)
			for instance in instances
		):
			thread.wait()
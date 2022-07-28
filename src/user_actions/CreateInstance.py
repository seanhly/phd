from requests import get
from user_actions.RunWorkerServices import RunWorkerServices
from user_actions.UserAction import UserAction
from cloud.server.Instance import Instance
from cloud.server.Pool import Pool
from cloud.vendors.Vultr import Vultr
from constants import PHD_LABEL
import time
from socket import socket, AF_INET, SOCK_STREAM
from datetime import datetime
from typing import List
from constants import BOOTSTRAP_SCRIPT
from util.ssh_do import ssh_do
from util.redis import get_neighbour, set_neighbours

import random
POSITION_KEYS = {
	-2: "L2",
	-1: "L",
	+1: "R",
	+2: "R2",
}

class CreateInstance(UserAction):
	@classmethod
	def command(cls) -> str:
		return "new"

	@classmethod
	def description(cls):
		return "Create an instance"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		current_pool = Pool.load(Vultr)
		count = int(self.query.strip()) if self.query else 1
		previous_instance_ips = [i.main_ip for i in Vultr.list_instances(label=PHD_LABEL)]
		new_instances: List[Instance] = []
		for i in range(count):
			new_instances.append(Vultr.create_instance(min_ram=2000))
		start = datetime.now().timestamp()
		incomplete_server = True
		while incomplete_server:
			print(f"\rAwaiting activation [{int(datetime.now().timestamp() - start)}s] ", end="")
			incomplete_server = False
			i = 0
			while i < len(new_instances) and not incomplete_server:
				instance_state = Vultr.get_instance(new_instances[i].id)
				if (
					not instance_state.main_ip
					or instance_state.main_ip == "0.0.0.0"
					or not instance_state.v6_main_ip
					or instance_state.v6_main_ip == "::"
					or not instance_state.internal_ip
					or instance_state.internal_ip == "0.0.0.0"
					or instance_state.status != "active"
				):
					incomplete_server = True
				else:
					new_instances[i] = instance_state
				i += 1
			time.sleep(1)
		print()
		current_pool.add_all(new_instances)
		new_instance_ips = [i.main_ip for i in new_instances]
		start = datetime.now().timestamp()
		ssh_closed = True
		while ssh_closed:
			print(f"\rAwaiting SSH access [{int(datetime.now().timestamp() - start)}s] ", end="")
			ssh_closed = False
			i = 0
			while i < len(new_instance_ips) and not ssh_closed:
				try:
					address = (new_instance_ips[i], 22)
					s = socket(AF_INET, SOCK_STREAM)
					s.connect(address)
					s.shutdown(2)
				except Exception:
					ssh_closed = True
					time.sleep(1)
				i += 1
		print()
		threads = []
		for previous_ip in previous_instance_ips:
			print(f"Allow access from {previous_ip} to new workers.")
			ssh_do(previous_ip, (
				f"/usr/sbin/ufw allow from {new_ip}"
				for new_ip in new_instance_ips
			), threads)
		for new_ip in new_instance_ips:
			print(f"Installing worker software on {new_ip}.")
			ssh_do(new_ip, BOOTSTRAP_SCRIPT, threads)
		for thread in threads:
			thread.wait()
		single_thread_instances: List[str]
		double_thread_instances: List[str]
		if len(previous_instance_ips) == 0:
			single_thread_instances = new_instance_ips
			double_thread_instances = single_thread_instances
			loop_single = 1
			loop_double = 2
		elif len(previous_instance_ips) == 1:
			single_thread_instances = [*new_instance_ips, previous_instance_ips[0]]
			double_thread_instances = single_thread_instances
			loop_single = 1
			loop_double = 2
		elif len(previous_instance_ips) == 2:
			single_thread_instances = [
				previous_instance_ips[-1],
				*new_instance_ips,
				previous_instance_ips[0],
			]
			double_thread_instances = single_thread_instances
			loop_single = 0
			loop_double = 2
		elif len(previous_instance_ips) == 3:
			single_thread_instances = [
				previous_instance_ips[-1],
				*new_instance_ips,
				previous_instance_ips[0],
			]
			double_thread_instances = [
				previous_instance_ips[2],
				*new_instance_ips,
				previous_instance_ips[0],
				previous_instance_ips[1],
			]
			loop_single = 0
			loop_double = 1
		elif len(previous_instance_ips) >= 4:
			any_previous_instance_ip = random.choice(list(previous_instance_ips))
			neighbourhood = [
				get_neighbour(any_previous_instance_ip, -1, firewall=True),
				any_previous_instance_ip,
				get_neighbour(any_previous_instance_ip, 1, firewall=True),
				get_neighbour(any_previous_instance_ip, 2, firewall=True),
			]
			single_thread_instances = [
				neighbourhood[1],
				*new_instance_ips,
				neighbourhood[2],
			]
			double_thread_instances = [
				neighbourhood[0],
				neighbourhood[1],
				*new_instance_ips,
				neighbourhood[2],
				neighbourhood[3],
			]
			loop_single = 0
			loop_double = 0
		threads = []
		for i in range(1 - loop_single, len(single_thread_instances)):
			threads += set_neighbours(
				single_thread_instances[i - 1],
				1,
				single_thread_instances[i],
				firewall=True,
			)
		for i in range(2 - loop_double, len(double_thread_instances)):
			threads += set_neighbours(
				double_thread_instances[(i - 2) % len(double_thread_instances)],
				2,
				double_thread_instances[i],
				firewall=True,
			)
		for thread in threads:
			thread.wait()	
		print("Installed worker software.")
		threads = []
		for new_ip in new_instance_ips:
			RunWorkerServices.run_on_host(new_ip, threads=threads)
		for thread in threads:
			thread.wait()
		threads = []
		for new_ip in new_instance_ips:
			print(f"Allow access from {new_ip} to previous workers.")
			ssh_do(new_ip, (
				f"/usr/sbin/ufw allow from {previous_ip}"
				for previous_ip in previous_instance_ips
			), threads)
			print(f"Allow access from {new_ip} to other new workers.")
			other_ips = [
				other_ip
				for other_ip in new_instance_ips
				if other_ip != new_ip
			]
			ssh_do(new_ip, (
				f"/usr/sbin/ufw allow from {other_ip}"
				for other_ip in other_ips
			), threads)
		for thread in threads:
			thread.wait()
		grobid_down = True
		start = datetime.now().timestamp()
		while grobid_down:
			print(f"\rAwaiting GROBID access [{int(datetime.now().timestamp() - start)}s] ", end="")
			grobid_down = False
			i = 0
			while i < len(new_instance_ips) and not grobid_down:
				response = get(f"http://{new_instance_ips[i]}/grobid/api/isalive")
				if response.status_code != 200 or (response.content or b"").decode().strip() != "true":
					grobid_down = True
					time.sleep(1)
				i += 1
		print()
		current_pool.dump()
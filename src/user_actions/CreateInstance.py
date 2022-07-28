from subprocess import Popen
from user_actions.ConnectGarageWorkers import ConnectGarageWorkers
from user_actions.StartWorker import StartWorker
from user_actions.UserAction import UserAction
from cloud.server.Instance import Instance
from cloud.server.Pool import Pool
from cloud.vendors.Vultr import Vultr
from constants import PHD_LABEL, UFW_BINARY
import time
from socket import socket, AF_INET, SOCK_STREAM
from datetime import datetime
from typing import List
from constants import BOOTSTRAP_SCRIPT
from util.ssh_do import ssh_do
from util.wait_then_clear import wait_then_clear
from util.redis import extend_network

class CreateInstance(UserAction):
	@classmethod
	def command(cls) -> str:
		return "new"

	@classmethod
	def description(cls):
		return "Create one or more instances"

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
			time.sleep(0.3)
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
					time.sleep(0.3)
				i += 1
		print()
		threads: List[Popen] = []
		# Bootstrap a system onto each worker.
		for new_ip in new_instance_ips:
			threads.append(ssh_do(new_ip, BOOTSTRAP_SCRIPT))
		wait_then_clear(threads)
		# New workers can now reach pre-existing workers.
		# <---|
		for previous_ip in previous_instance_ips:
			ssh_do(previous_ip, (
				f"{UFW_BINARY} allow from {new_ip}"
				for new_ip in new_instance_ips
			), threads)
		set(previous_instance_ips + new_instance_ips)
		# New workers can now reach each other.
		# | <-->
		for new_ip in new_instance_ips:
			ssh_do(new_ip, (
				f"{UFW_BINARY} allow from {new_ip}"
				for new_ip in new_instance_ips
			), threads)
		# Pre-existing workers can now reach new workers.
		# |--->
		for new_ip in new_instance_ips:
			ssh_do(new_ip, (
				f"{UFW_BINARY} allow from {previous_ip}"
				for previous_ip in previous_instance_ips
			), threads)
		for previous_ip in previous_instance_ips:
			threads.append(extend_network(previous_ip, new_instance_ips, True))
		for new_ip in new_instance_ips:
			threads.append(extend_network(new_ip, new_instance_ips + previous_instance_ips, True))
		wait_then_clear(threads)
		# Run each worker.
		for new_ip in new_instance_ips:
			threads.append(StartWorker.run_on_host(new_ip))
		wait_then_clear(threads)
from subprocess import Popen
from user_actions.StartWorker import StartWorker
from user_actions.UserAction import UserAction
from cloud.server.Pool import Pool
from cloud.vendors.Vultr import Vultr
from constants import PHD_LABEL, UFW_BINARY
from typing import List
from constants import BOOTSTRAP_SCRIPT
from util.ssh_do import ssh_do
from util.wait_then_clear import wait_then_clear
from util.redis import extend_network, set_region_and_public_ipv4

class CreateInstanceOnIPs(UserAction):
	@classmethod
	def command(cls) -> str:
		return "new-2"

	@classmethod
	def description(cls):
		return "Set up an instance on a pre-created IP."

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		# New IPs are fed in as arguments.
		# Details for these IPs are then pulled from the Pool cache.
		new_instances = [
			instance
			for instance in Pool.load(Vultr).pool
			if instance.main_ip not in self.ip_arguments
		]
		new_instance_ips = {i.main_ip for i in new_instances}
		threads: List[Popen] = []
		# Bootstrap a system onto each worker.
		for new_ip in new_instance_ips:
			threads.append(ssh_do(new_ip, BOOTSTRAP_SCRIPT))
		wait_then_clear(threads)
		previous_instance_ips = [i.main_ip for i in Vultr.list_instances(label=PHD_LABEL)]
		# New workers can now reach pre-existing workers.
		# <---|
		for previous_ip in previous_instance_ips:
			ssh_do(previous_ip, (
				f"{UFW_BINARY} allow from {new_ip}"
				for new_ip in new_instance_ips
			), threads)
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
			threads.append(extend_network(new_ip, set(previous_instance_ips).union(new_instance_ips), True))
		for new_instance in new_instances:
			threads.append(
				set_region_and_public_ipv4(
					new_instance.main_ip,
					new_instance.region,
					new_instance.main_ip,
				)
			)
		wait_then_clear(threads)
		# Run each worker.
		for new_ip in new_instance_ips:
			threads.append(StartWorker.run_on_host(new_ip))
		wait_then_clear(threads)
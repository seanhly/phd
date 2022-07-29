from arguments.IPArgument import IPArgument
from user_actions.CreateInstanceOnIPs import CreateInstanceOnIPs
from user_actions.UserAction import UserAction
from cloud.server.Instance import Instance
from cloud.server.Pool import Pool
from cloud.vendors.Vultr import Vultr
from constants import PHD_LABEL
import time
from socket import socket, AF_INET, SOCK_STREAM
from datetime import datetime
from typing import List

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
		new_instance_ips = {i.main_ip for i in new_instances}
		start = datetime.now().timestamp()
		ssh_closed = True
		while ssh_closed:
			print(f"\rAwaiting SSH access [{int(datetime.now().timestamp() - start)}s] ", end="")
			ssh_closed = False
			for new_ip in new_instance_ips:
				try:
					address = (new_ip, 22)
					s = socket(AF_INET, SOCK_STREAM)
					s.connect(address)
					s.shutdown(2)
				except Exception:
					ssh_closed = True
					time.sleep(0.3)
					break
		print()
		current_pool.add_all(new_instances)
		current_pool.dump()
		CreateInstanceOnIPs([
			IPArgument(new_instance.main_ip)
			for new_instance in new_instances
		]).execute()
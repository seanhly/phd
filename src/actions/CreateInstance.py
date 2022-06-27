from regex import P
from actions.Action import Action
from cloud.server.Pool import Pool
from cloud.vendors.Vultr import Vultr
from constants import POOL_LABEL
import time
from socket import socket, AF_INET, SOCK_STREAM
from datetime import datetime
import traceback


class CreateInstance(Action):
	@classmethod
	def command(cls) -> str:
		return "create-instance"

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
		count = int(self.query.strip())
		previous_instances = Vultr.list_instances(label=POOL_LABEL)
		new_instances = []
		for i in range(count):
			new_instances.append(Vultr.create_instance(min_ram=2000))
		for i in previous_instances:
			print(str(i))
		start = datetime.now().timestamp()
		incomplete_server = True
		while incomplete_server:
			print(f"\rAwaiting activation [{int(datetime.now().timestamp() - start)}s] ", end="")
			incomplete_server = False
			i = 0
			instance_states = []
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
					instance_states.append(instance_state)
				i += 1
			time.sleep(1)
		print()
		start = datetime.now().timestamp()
		ssh_closed = True
		while ssh_closed:
			print(f"\rAwaiting SSH access [{int(datetime.now().timestamp() - start)}s] ", end="")
			s = socket(AF_INET, SOCK_STREAM)
			ssh_closed = False
			i = 0
			while i < len(instance_states) and not ssh_closed:
				try:
					s.connect((instance_states[i].main_ip, 22))
					s.shutdown(2)
				except Exception as e:
					traceback.print_exc()
					ssh_closed = True
					time.sleep(1)
				i += 1
		print()
		instance_state.install()
		instance_state.run_grobid()
		current_pool += new_instances
		current_pool.dump()
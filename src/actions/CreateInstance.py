from regex import P
from actions.Action import Action
from cloud.server.Pool import Pool
from cloud.vendors.Vultr import Vultr
from constants import POOL_LABEL
import time
from socket import socket, AF_INET, SOCK_STREAM
from datetime import datetime


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
		instance = Vultr.create_instance(min_ram=2000)
		current_pool.add(instance)
		vendor = Vultr
		instances = vendor.list_instances(label=POOL_LABEL)
		for i in instances:
			print(str(i))
		start = datetime.now().timestamp()
		while True:
			print(f"\rAwaiting activation [{int(datetime.now().timestamp() - start)}s] ", end="")
			instance_state = vendor.get_instance(instance.id)
			if (
				instance_state.main_ip
				and instance_state.main_ip != "0.0.0.0"
				and instance_state.v6_main_ip
				and instance_state.v6_main_ip != "::"
				and instance_state.internal_ip
				and instance_state.internal_ip != "0.0.0.0"
				and instance_state.status == "active"
			):
				break
			time.sleep(1)
		print()
		start = datetime.now().timestamp()
		while True:
			print(f"\rAwaiting SSH access [{int(datetime.now().timestamp() - start)}s] ", end="")
			s = socket(AF_INET, SOCK_STREAM)
			try:
				s.connect((instance_state.main_ip, 22))
				s.shutdown(2)
				break
			except:
				time.sleep(1)
		print()
		instance_state.install()
		instance_state.run_grobid()
from actions.Action import Action
from cloud.server.Pool import Pool
from cloud.vendors.Vultr import Vultr
from constants import POOL_LABEL


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
from user_actions.UserAction import UserAction
from cloud.server.Pool import Pool
from cloud.vendors.Vultr import Vultr
from constants import POOL_LABEL


class ListInstances(UserAction):
	@classmethod
	def command(cls) -> str:
		return "ls"

	@classmethod
	def description(cls):
		return "List server instances"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		vendor = Vultr
		instances = vendor.list_instances(label=POOL_LABEL)
		Pool.load(vendor).update(instances)
		for i in instances:
			print(str(i))
from user_actions.UserAction import UserAction
from cloud.vendors.Vultr import Vultr
from cloud.server.Pool import Pool
from constants import PHD_LABEL


class DestroyInstances(UserAction):
	@classmethod
	def command(cls) -> str:
		return "rma"

	@classmethod
	def description(cls):
		return "Destroy all server instances"

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
		for instance in Vultr.list_instances(label=PHD_LABEL):
			instance.destroy()
			current_pool.remove(instance.id)
		current_pool.dump()

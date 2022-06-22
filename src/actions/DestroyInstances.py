from actions.Action import Action
from cloud.vendors.Vultr import Vultr
from constants import POOL_LABEL


class DestroyInstances(Action):
	@classmethod
	def command(cls) -> str:
		return "destroy-instances"

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
		for i in Vultr.list_instances(label=POOL_LABEL):
			i.destroy()
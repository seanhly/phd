from actions.Action import Action
from cloud.vendors.Vultr import Vultr


class ListInstances(Action):
	@classmethod
	def command(cls) -> str:
		return "instances"

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
		#for i in Vultr.list_instances(label=POOL_LABEL):
		for i in Vultr.list_instances():
			print(str(i))
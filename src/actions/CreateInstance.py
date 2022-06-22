from actions.Action import Action
from cloud.vendors.Vultr import Vultr


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
		print(str(Vultr.create_instance()))
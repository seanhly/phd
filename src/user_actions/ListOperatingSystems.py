from user_actions.UserAction import UserAction
from cloud.vendors.Vultr import Vultr


class ListOperatingSystems(UserAction):
	@classmethod
	def command(cls) -> str:
		return "ls-os"

	@classmethod
	def description(cls):
		return "List available cloud operating systems"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		for os in Vultr.list_operating_systems():
			print(str(os))

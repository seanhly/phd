from user_actions.UserAction import UserAction
from uuid import getnode

class PrintMacAddress(UserAction):
	@classmethod
	def command(cls) -> str:
		return "mac"

	@classmethod
	def description(cls):
		return "Print the instance's mac address."

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		print(getnode())
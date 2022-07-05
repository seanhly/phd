from user_actions.UserAction import UserAction
from uuid import getnode
from JSON import JSON

class PrintSystemInfoJSON(UserAction):
	@classmethod
	def command(cls) -> str:
		return "info.json"

	@classmethod
	def description(cls):
		return "Print the instance's system info as JSON."

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		print(JSON.dumps(dict(
			mac=getnode()
		)))
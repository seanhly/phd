from user_actions.UserAction import UserAction


class RedistributeWork(UserAction):
	@classmethod
	def command(cls) -> str:
		return "redistribute"

	@classmethod
	def description(cls):
		return "Redistribute work across neighbouring worker nodes"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		print("TODO")
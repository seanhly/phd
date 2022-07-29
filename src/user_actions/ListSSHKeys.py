from user_actions.UserAction import UserAction
from cloud.vendors.Vultr import Vultr


class ListSSHKeys(UserAction):
	@classmethod
	def command(cls) -> str:
		return "ls-ssh"

	@classmethod
	def description(cls):
		return "List available SSH keys"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		for ssh in Vultr.list_ssh_keys():
			print(str(ssh))

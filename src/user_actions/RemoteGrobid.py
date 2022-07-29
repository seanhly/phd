from user_actions.UserAction import UserAction
from cloud.server.Pool import Pool
from cloud.vendors.Vultr import Vultr


class RemoteGrobid(UserAction):
	@classmethod
	def command(cls) -> str:
		return "remote-grobid"

	@classmethod
	def description(cls):
		return "Run the GROBID server remotely"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		pool = Pool.load(Vultr)
		pool.run_grobid()

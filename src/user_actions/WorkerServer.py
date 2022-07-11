from typing import Dict, Type
from redis import Redis
from user_actions import UserAction
from constants import REDIS_WORKER_NETWORK_DB


class WorkerServer(UserAction):
	@classmethod
	def command(cls) -> str:
		return "worker-server"

	@classmethod
	def description(cls):
		return "Run the worker's server."

	def recognised_options(self):
		return {}

	def arg_options(self):
		return {}

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		r = Redis(db=REDIS_WORKER_NETWORK_DB)
		pubsub = r.pubsub()
		pubsub.subscribe("user-actions-channel")
		user_actions: Dict[str, Type[UserAction]] = {
			T.command(): T
			for T in UserAction.__subclasses__()
		}
		for a in pubsub.listen():
			if a["type"] == "message":
				queue = a["data"].decode()
				if queue in user_actions:
					user_actions[queue]().execute()
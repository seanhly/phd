from typing import Dict, Type
from redis import Redis
from worker_actions import WorkerAction
from user_actions import UserAction
from constants import REDIS_WORK_QUEUES_DB


class Work(UserAction):
	@classmethod
	def command(cls) -> str:
		return "work"

	@classmethod
	def description(cls):
		return "Set the node indefinitely working."

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		r = Redis(db=REDIS_WORK_QUEUES_DB)
		work_queues = r.keys()
		worker_actions: Dict[str, Type[WorkerAction]] = {
			T.queue_name(): T
			for T in WorkerAction.__subclasses__()
		}
		for work_queue in map(bytes.decode, work_queues):
			TheWorkerAction = worker_actions.get(work_queue)
			if TheWorkerAction:
				work_order = r.spop(work_queue)
				worker_action = TheWorkerAction(work_order)
				for NextWorkerAction, orders in worker_action.execute():
					r.sadd(
						NextWorkerAction.queue_name(),
						*orders
					)

from typing import Dict, Type
from redis import Redis
from worker_actions import WorkerAction
from user_actions import UserAction
from constants import REDIS_WORK_QUEUES_DB

QUEUE_OPTION = "queue"
PRE_PUSH_OPTION = "pre-push"


class Work(UserAction):
	@classmethod
	def command(cls) -> str:
		return "work"

	@classmethod
	def description(cls):
		return "Set the node indefinitely working."

	def recognised_options(self):
		return {QUEUE_OPTION, PRE_PUSH_OPTION}

	def arg_options(self):
		return {QUEUE_OPTION, PRE_PUSH_OPTION}

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		print("Connecting to: ", REDIS_WORK_QUEUES_DB)
		r = Redis(db=REDIS_WORK_QUEUES_DB)
		if self.options and PRE_PUSH_OPTION in self.options:
			pre_push_value = self.options[PRE_PUSH_OPTION]
			queue = self.options[QUEUE_OPTION]
			print(queue, pre_push_value)
			r.sadd(queue, pre_push_value)
		else:
			queue = None
		work_queues = r.keys()
		worker_actions: Dict[str, Type[WorkerAction]] = {
			T.queue_name(): T
			for T in WorkerAction.__subclasses__()
			if not queue or queue == T.queue_name() 
		}
		for work_queue in map(bytes.decode, work_queues):
			TheWorkerAction = worker_actions.get(work_queue)
			if TheWorkerAction:
				if TheWorkerAction.one_at_a_time():
					work_order = r.spop(work_queue)
					worker_action = TheWorkerAction(work_order)
				else:
					worker_action = TheWorkerAction()
				for NextWorkerAction, orders in worker_action.execute():
					r.sadd(
						NextWorkerAction.queue_name(),
						*orders
					)

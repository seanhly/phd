from typing import Dict, Type
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
		from redis import Redis
		r = Redis(db=REDIS_WORK_QUEUES_DB)
		if self.options and PRE_PUSH_OPTION in self.options:
			pre_push_value = self.options[PRE_PUSH_OPTION]
			queue = self.options[QUEUE_OPTION]
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
			the_worker_action = worker_actions.get(work_queue)
			if the_worker_action:
				if the_worker_action.one_at_a_time():
					work_order = r.spop(work_queue)
					worker_action = the_worker_action(work_order)
				else:
					worker_action = the_worker_action(None)
				# This is where the magic happens.
				for NextWorkerAction, orders in worker_action.execute():
					r.sadd(
						NextWorkerAction.queue_name(),
						*orders
					)

from user_actions.UserAction import UserAction


from typing import Dict, List, Set, Tuple, Type
from redis import Redis
from util.redis import get_neighbourhood
from worker_actions import WorkerAction
from user_actions import UserAction
from constants import REDIS_WORK_QUEUES_DB

QUEUE_OPTION = "queue"
PRE_PUSH_OPTION = "pre-push"


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
		worker_actions: Dict[str, Type[WorkerAction]] = {
			T.queue_name(): T
			for T in WorkerAction.__subclasses__()
		}
		the_neighbourhood = get_neighbourhood()
		neighbourhood_queue_lengths: Dict[str, Dict[str, int]] = {}
		total_queue_lengths: Dict[str, int] = {}
		for work_queue, TheWorkerAction in worker_actions.items():
			neighbourhood_queue_lengths[work_queue] = {}
			total_queue_lengths[work_queue] = 0
		for host in the_neighbourhood:
			r = Redis(db=REDIS_WORK_QUEUES_DB, host=host)
			for work_queue, TheWorkerAction in worker_actions.items():
				if TheWorkerAction.one_at_a_time():
					worker_order_count = r.scard(work_queue)
					total_queue_lengths[work_queue] = (
						total_queue_lengths.get(work_queue, 0)
						+ worker_order_count
					)
					neighbourhood_queue_lengths[work_queue][host] = worker_order_count
		for work_queue, total in total_queue_lengths.items():
			if total > 0:
				the_neighbourhood_queue_lengths = neighbourhood_queue_lengths[work_queue]
				min_orders_per_node = total // len(the_neighbourhood_queue_lengths)
				max_orders_per_node = min_orders_per_node + 1
				nodes_with_one_added_order = total % len(the_neighbourhood_queue_lengths)
				nodes_with_one_less_order = (
					len(the_neighbourhood_queue_lengths)
					- nodes_with_one_added_order
				)
				for ip, orders in the_neighbourhood_queue_lengths.items():
					if orders == min_orders_per_node:
						if nodes_with_one_less_order:
							nodes_with_one_less_order -= 1
							del the_neighbourhood_queue_lengths[ip]
					elif orders == max_orders_per_node:
						if nodes_with_one_added_order:
							nodes_with_one_added_order -= 1
							del the_neighbourhood_queue_lengths[ip]
				# change size needed => [
				#     receive (-): [ip, bool: whether change would make node hard-worker]
				#     give (+): [ip, bool: whether change would make node hard-worker]
				# ]
				changes_needed: Dict[str, int] = {}
				order_pool = []
				for ip, orders in the_neighbourhood_queue_lengths.items():
					if nodes_with_one_added_order:
						change = max_orders_per_node - orders
						nodes_with_one_added_order -= 1
					elif nodes_with_one_less_order:
						change = min_orders_per_node - orders
						nodes_with_one_less_order -= 1
					if change < 0:
						r = Redis(db=REDIS_WORK_QUEUES_DB, host=ip)
						task_pool += r.spop(work_queue, -change)
					else:
						changes_needed[ip] = change
				for ip, changes in changes_needed.items():
					r = Redis(db=REDIS_WORK_QUEUES_DB, host=ip)
					to_add = []
					for _ in range(changes):
						to_add.append(order_pool.pop())
					task_pool += r.sadd(work_queue, *to_add)
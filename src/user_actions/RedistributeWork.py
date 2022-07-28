from user_actions.UserAction import UserAction
from typing import Any, Dict, List, Set, Tuple, Type
from redis import Redis
from util.redis import get_network
from worker_actions import WorkerAction
from user_actions import UserAction
from constants import REDIS_WORK_QUEUES_DB, REDIS_WORKER_NETWORK_DB
from uuid import getnode

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
		mac_id = getnode()
		neighbourhood_work_queues: Dict[int, Redis] = {}
		neighbourhood_lock_queues: Dict[int, Redis] = {}
		neighbourhood = get_neighbourhood()
		for relation, host in neighbourhood.items():
			lock_queue = Redis(db=REDIS_WORKER_NETWORK_DB, host=host)
			if lock_queue.set("lock", mac_id, ex=300, nx=True):
				neighbourhood_lock_queues[relation] = lock_queue
				neighbourhood_work_queues[relation] = Redis(db=REDIS_WORK_QUEUES_DB, host=host)
		modified: Set[int] = set()
		if len(neighbourhood_work_queues) >= 2:
			total_queue_lengths: Dict[str, int] = {}
			neighbourhood_queue_lengths: Dict[str, Dict[int, int]] = {}
			for work_queue, TheWorkerAction in worker_actions.items():
				neighbourhood_queue_lengths[work_queue] = {}
				total_queue_lengths[work_queue] = 0
			for relation, connection in neighbourhood_work_queues.items():
				for work_queue, TheWorkerAction in worker_actions.items():
					if TheWorkerAction.one_at_a_time():
						worker_order_count = connection.hlen(work_queue)
						total_queue_lengths[work_queue] = (
							total_queue_lengths.get(work_queue, 0)
							+ worker_order_count
						)
						neighbourhood_queue_lengths[work_queue][relation] = worker_order_count
			for work_queue, total in total_queue_lengths.items():
				if total > 0:
					the_neighbourhood_queue_lengths = neighbourhood_queue_lengths[work_queue]
					l = len(the_neighbourhood_queue_lengths)
					min_orders_per_node = total // l
					max_orders_per_node = min_orders_per_node + 1
					nodes_with_one_added_order = total % l
					nodes_with_one_less_order = (l - nodes_with_one_added_order)
					for relation, orders in list(the_neighbourhood_queue_lengths.items()):
						if orders == min_orders_per_node:
							if nodes_with_one_less_order:
								nodes_with_one_less_order -= 1
								del the_neighbourhood_queue_lengths[relation]
						elif orders == max_orders_per_node:
							if nodes_with_one_added_order:
								nodes_with_one_added_order -= 1
								del the_neighbourhood_queue_lengths[relation]
					changes_needed: Dict[str, int] = {}
					order_pool: List[Tuple[str, Any, int]] = []
					for relation, orders in the_neighbourhood_queue_lengths.items():
						if nodes_with_one_added_order:
							changes = max_orders_per_node - orders
							nodes_with_one_added_order -= 1
						elif nodes_with_one_less_order:
							changes = min_orders_per_node - orders
							nodes_with_one_less_order -= 1
						if changes > 0:
							changes_needed[relation] = changes
						else:
							connection = neighbourhood_work_queues[relation]
							for raw_job, raw_metadata in connection.hscan_iter(name=work_queue):
								connection.hdel(work_queue, job)
								order_pool.append((
									raw_job.decode(),
									raw_metadata.decode(),
									relation
								))
								changes += 1
								if changes == 0:
									break
							modified.add(relation)
					for relation, changes in changes_needed.items():
						jobs = {}
						for _ in range(changes):
							job, payload, relation = order_pool.pop()
							jobs[job] = payload
						neighbourhood_work_queues[relation].hmset(work_queue, jobs)
						modified.add(relation)
		for connection in neighbourhood_lock_queues.values():
			connection.delete("lock")
		if modified:
			to_update = {min(modified), max(modified)} - {0}
			for relation in to_update:
				host: str = neighbourhood[relation]
				RedistributeWork.remote(host)
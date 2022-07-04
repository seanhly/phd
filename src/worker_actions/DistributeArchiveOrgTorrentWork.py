from typing import Dict, Set
from worker_actions.WorkerAction import WorkerAction
from util.redis import get_neighbours
from redis import Redis
from constants import REDIS_WORK_QUEUES_DB


class DistributeArchiveOrgTorrentWork(WorkerAction):
	@classmethod
	def queue_name(cls) -> str:
		return "archive.org-torrents"

	@classmethod
	def description(cls) -> str:
		return "Distribute the archive.org torrent work."

	def execute(self):
		the_neighbours = get_neighbours()
		far_left_neighbour = the_neighbours[-2]
		far_right_neighbour = the_neighbours[2]
		host_to_ids: Dict[str, Set[str]] = {
			host: Redis(
				host=host,
				db=REDIS_WORK_QUEUES_DB,
			).smembers(DistributeArchiveOrgTorrentWork.queue_name())
			for host in (None, *set(the_neighbours.values()))
		}
		all_ids = sorted(set(
			id
			for id_set in host_to_ids.values()
			for id in id_set
		))

		return ()
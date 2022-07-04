from sys import stdout
from typing import Dict, Set
from worker_actions.WorkerAction import WorkerAction
from util.redis import get_neighbours
from redis import Redis
from constants import REDIS_WORK_QUEUES_DB
from user_actions.PrintMacAddress import PrintMacAddress


class DistributeArchiveOrgTorrentWork(WorkerAction):
	@classmethod
	def queue_name(cls) -> str:
		return "archive.org-torrents"

	@classmethod
	def description(cls) -> str:
		return "Distribute the archive.org torrent work."

	def execute(self):
		the_neighbours = get_neighbours()
		neighbour_ips = sorted(set(the_neighbours.values()))
		host_to_ids: Dict[str, Set[str]] = {
			host: Redis(
				host=host,
				db=REDIS_WORK_QUEUES_DB,
			).smembers(DistributeArchiveOrgTorrentWork.queue_name())
			for host in (None, *neighbour_ips)
		}
		mac_addresses = {
			ip: mac if mac else PrintMacAddress.remote(ip, stdout=True).stdout.read().strip()
			for ip, mac in zip(
				neighbour_ips,
				Redis().hmget("mac-addresses", *neighbour_ips),
			)
		}
		print(mac_addresses)
		all_ids = sorted(set(
			id
			for id_set in host_to_ids.values()
			for id in id_set
		))

		return ()
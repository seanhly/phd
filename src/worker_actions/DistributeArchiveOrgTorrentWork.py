from typing import Dict, Set

from requests import get
from worker_actions.WorkerAction import WorkerAction
from util.redis import get_neighbours
from redis import Redis
from constants import REDIS_WORK_QUEUES_DB
from JSON import JSON
from uuid import getnode


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
		

		r = Redis()
		mac_addresses = r.hmget("mac-addresses", *neighbour_ips)
		mac_to_ip: Dict[str, int] = {}
		set_later: Dict[str, int] = {}
		local_mac = getnode()
		for ip, mac in zip(
			neighbour_ips,
			(
				int(ma.decode().strip())
				if ma
				else None
				for ma in mac_addresses
			),
		):
			# Because when the network is small (<=2), a neighbour could be
			# the local worker node itself.
			if mac != local_mac:
				if mac:
					mac_to_ip[mac] = ip
				else:
					mac = JSON.loads(
						get(
							f"http://{ip}/system-info.json"
						).content.decode()
					)["mac"]
					if mac != local_mac:
						set_later[mac] = ip
		if set_later:
			r.hmset("mac-addresses", set_later)
			mac_to_ip.update(set_later)
			print(set_later)
		mac_to_ip[local_mac]
		sorted_ips = sorted(mac_to_ip.items())
		print(sorted_ips)
		all_ids = sorted(set(
			id
			for id_set in host_to_ids.values()
			for id in id_set
		))
		print(all_ids)

		return ()

	@classmethod
	def one_at_a_time(cls) -> bool:
		False
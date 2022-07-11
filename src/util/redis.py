from typing import Dict, Optional, Set
from constants import REDIS_WORKER_NETWORK_DB
from constants import INSTALL_SCRIPT_URL
from util.ssh_do import ssh_do
from redis import Redis

INSTALL_SCRIPT = f"sh -c \"$(wget {INSTALL_SCRIPT_URL} -O -)\""
POSITION_KEYS = {
	-2: "L2",
	-1: "L",
	+1: "R",
	+2: "R2",
}

def set_neighbour(a: str, position: int, b: str, firewall: bool):
	if firewall:
		return ssh_do(
			a,
			f"/usr/bin/redis-cli -n {REDIS_WORKER_NETWORK_DB}",
			stdin=f"set {POSITION_KEYS[position]} {b}",
		)
	else:
		Redis(
			host=a,
			db=REDIS_WORKER_NETWORK_DB,
		).set(POSITION_KEYS[position], b)
		return None

def get_neighbour(host: Optional[str], position: int, firewall = False) -> str:
	if firewall:
		process = ssh_do(
			host,
			f"/usr/bin/redis-cli -n {REDIS_WORKER_NETWORK_DB}",
			stdin=f"get {POSITION_KEYS[position]}",
			stdout=True,
		)
		return process.stdout.read().decode().strip()
	else:
		return Redis(
			host=host,
			db=REDIS_WORKER_NETWORK_DB,
		).get(POSITION_KEYS[position]).decode().strip()

def get_neighbours(host: str = None, firewall = False) -> Dict[int, str]:
	neighbour_offsets = list(POSITION_KEYS.keys())
	position_keys = (POSITION_KEYS[offset] for offset in neighbour_offsets)
	if firewall:
		return dict(zip(
			neighbour_offsets,
			ssh_do(
				host,
				f"/usr/bin/redis-cli -n {REDIS_WORKER_NETWORK_DB}",
				stdin=f"mget {' '.join(*position_keys)}",
				stdout=True,
			).stdout.read().decode().strip().split("\n"),
		))
	else:
		return dict(zip(
			neighbour_offsets,
			[
				result.decode().strip() if result else None
				for result in Redis(
					host=host,
					db=REDIS_WORKER_NETWORK_DB,
				).mget(*position_keys)
			],
		))

def get_neighbourhood(host: str = None, firewall = False) -> Set[Optional[str]]:
	the_neighbours = get_neighbours(host, firewall)
	ips = set(the_neighbours.values())
	if len(ips) == 1:
		# Single node network
		return {None}
	if len(ips) == 2:
		if the_neighbours[1] == the_neighbours[-1]:
			# Single edge network
			return {the_neighbours[1], None}
		# Triangle network
		return {the_neighbours[1], the_neighbours[-1], None}
	if len(ips) == 3:
		# Square network
		return {the_neighbours[1], the_neighbours[-1], the_neighbours[2], None}
	# Pentagonal+ network
	return {*the_neighbours.values(), None}

def set_neighbours(a: str, position: int, b: str, firewall = False):
	return [
		p
		for p in (
			set_neighbour(a, position, b, firewall),
			set_neighbour(b, -position, a, firewall),
		)
		if p
	]
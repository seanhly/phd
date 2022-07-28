from typing import Iterable, Set
from constants import REDIS_CLI_BINARY, REDIS_WORKER_NETWORK_DB
from util.ssh_do import ssh_do

def extend_network(host: str, workers: Iterable[str], firewall: bool):
	workers = set(workers) - {host}
	if firewall:
		return ssh_do(
			host,
			f"{REDIS_CLI_BINARY} -n {REDIS_WORKER_NETWORK_DB}",
			stdin=f"sadd network {' '.join(workers)}",
		)
	else:
		from redis import Redis
		Redis(
			host=host,
			db=REDIS_WORKER_NETWORK_DB,
		).sadd("network", workers)
		return None

def remove_from_network(host: str, workers: Iterable[str], firewall: bool):
	workers = set(workers) - {host}
	if firewall:
		return ssh_do(
			host,
			f"{REDIS_CLI_BINARY} -n {REDIS_WORKER_NETWORK_DB}",
			stdin=f"srem network {' '.join(workers)}",
		)
	else:
		from redis import Redis
		Redis(
			host=host,
			db=REDIS_WORKER_NETWORK_DB,
		).srem("network", workers)
		return None

def get_network(host: str = None, firewall = False) -> Set[str]:
	if firewall:
		return set(ssh_do(
			host,
			f"{REDIS_CLI_BINARY} -n {REDIS_WORKER_NETWORK_DB}",
			stdin=f"smembers network",
			stdout=True,
		).stdout.read().decode().strip().split())
	else:
		from redis import Redis
		return {
			result.decode()
			for result in Redis(
				host=host,
				db=REDIS_WORKER_NETWORK_DB,
			).smembers("network")
		}
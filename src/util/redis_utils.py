from subprocess import Popen, check_output
from time import sleep
from typing import Iterable, Set
from constants import GARAGE_BINARY, REDIS_CLI_BINARY, REDIS_WORKER_NETWORK_DB
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


def get_network(host: str = None, firewall=False) -> Set[str]:
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


def set_garage_id():
    garage_id = None
    for _ in range(5):
        try:
            output = check_output([GARAGE_BINARY, "node", "id", "-q"])
            garage_id = output.decode().strip().split('@')[0]
            break
        except Exception as e:
            print(str(e))
            sleep(0.3)
    if not garage_id:
        raise Exception("couldn't find garage ID")
    from redis import Redis
    Redis(db=REDIS_WORKER_NETWORK_DB).set("garage-id", garage_id)


def await_garage_id(host: str = None) -> str:
    from redis import Redis
    garage_id = None
    while not garage_id:
        r = Redis(host=host, db=REDIS_WORKER_NETWORK_DB)
        garage_id = r.get("garage-id")
        sleep(0.3)

    return garage_id.decode().strip()


def set_region_and_public_ipv4(
        host: str, region: str, public_ipv4: str,
) -> Popen:
    return ssh_do(
        host,
        f"{REDIS_CLI_BINARY} -n {REDIS_WORKER_NETWORK_DB}",
        stdin=[
            f"set region {region}",
            f"set public-ipv4 {public_ipv4}",
        ],
        stdout=True,
    )


def get_region(host: str = None) -> str:
    from redis import Redis
    r = Redis(host=host, db=REDIS_WORKER_NETWORK_DB)
    return r.get("region").decode().strip()


def get_public_ipv4() -> str:
    from redis import Redis
    r = Redis(db=REDIS_WORKER_NETWORK_DB)
    return r.get("public-ipv4").decode().strip()

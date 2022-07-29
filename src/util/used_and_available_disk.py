from typing import Dict, Iterable, Tuple
from util.ssh_do import ssh_do


def used_and_available_disk(ips: Iterable[str]) -> Dict[str, Tuple[int, int]]:
    return {
        ip: tuple(
            int(b)
            for b in ssh_do(
                ip,
                "/usr/bin/df -B1 /",
                stdout=True,
            ).stdout.read().decode().strip().split("\n")[-1].split()[2:4]
        )
        for ip in ips
    }

import subprocess
from typing import List, Optional
from constants import PHD_PRIVATE_RSA_KEY, RSYNC_BINARY, SSH_BINARY

RSYNC_ARGS = (
	RSYNC_BINARY,
	"-Pav",
	"-e",
	f"{SSH_BINARY} -o  StrictHostKeyChecking=no -o "
	f"PasswordAuthentication=no -i {PHD_PRIVATE_RSA_KEY}"
)


def rsync_to(
	src_dir: str,
	host: str,
	dst_dir: str,
	threads: Optional[List[subprocess.Popen]] = None,
) -> Optional[subprocess.Popen]:
	p = subprocess.Popen([
		*RSYNC_ARGS,
		src_dir,
		f"root@{host}:{dst_dir}",
	])
	if threads is not None:
		threads.append(p)
	else:
		return p

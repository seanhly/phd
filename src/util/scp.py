import subprocess
from typing import Iterable, List, Optional, Union
from constants import PHD_PRIVATE_RSA_KEY

SCP_ARGS = (
	"/usr/bin/scp",
	"-o",
	"StrictHostKeyChecking=no",
	"-o",
	"PasswordAuthentication=no",
	"-i",
	PHD_PRIVATE_RSA_KEY,
)


def scp(
	src_files: Union[Iterable[str], str],
	host: str,
	dst_dir: str,
	threads: Optional[List[subprocess.Popen]] = None,
) -> Optional[subprocess.Popen]:
	if src_files:
		kwargs = {}
		p = subprocess.Popen(
			[
				*SCP_ARGS,
				*(
					(src_files,)
					if type(src_files) == str
					else src_files
				), f"root@{host}:{dst_dir}"
			],
			**kwargs
		)
		if threads is not None:
			threads.append(p)
		else:
			return p

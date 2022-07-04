import subprocess
from typing import Iterable, List, Optional, Union
from constants import PHD_PRIVATE_RSA_KEY

SSH_ARGS = (
	"/usr/bin/ssh",
	"-o",
	"StrictHostKeyChecking=no",
	"-o",
	"PasswordAuthentication=no",
	"-i",
	PHD_PRIVATE_RSA_KEY,
)


def ssh_do(
	host: str,
	things: Union[Iterable[str], str],
	threads: Optional[List[subprocess.Popen]] = None,
	stdin: Optional[Union[Iterable[str], str]] = None,
	stdout: bool = False
) -> Optional[subprocess.Popen]:
	if type(things) == str:
		cmd = things
	else:
		cmd = " && ".join(things)
	if cmd:
		kwargs = {}
		if stdin:
			kwargs["stdin"] = subprocess.PIPE
		if stdout:
			kwargs["stdout"] = subprocess.PIPE
		p = subprocess.Popen(
			[*SSH_ARGS, f"root@{host}", cmd],
			**kwargs
		)
		if stdin:
			if type(stdin) == str:
				p.stdin.write(bytes(stdin, encoding="utf8"))
			else:
				for line in stdin:
					p.stdin.write(bytes(line, encoding="utf8"))
			p.stdin.close()
		if threads is not None:
			threads.append(p)
		else:
			return p

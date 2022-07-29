from typing import List
from subprocess import Popen


def wait_then_clear(threads: List[Popen]) -> None:
	for t in threads:
		if t:
			t.wait()
	threads.clear()

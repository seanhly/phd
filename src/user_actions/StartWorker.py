from typing import Dict, List, Optional, Tuple
from user_actions.UserAction import UserAction
from constants import (
	COCKROACH_BINARY, COCKROACH_BINARY_NAME, COCKROACH_PORT,
	GARAGE_BINARY, GARAGE_BINARY_NAME, GROBID_DIR_PATH,
	GROBID_EXEC_PATH,
	TMUX_BINARY
)
from subprocess import Popen, call
from util.wait_then_clear import wait_then_clear
from socket import socket, AF_INET, SOCK_STREAM
import time


class StartWorker(UserAction):
	@classmethod
	def command(cls) -> str:
		return "start"

	@classmethod
	def description(cls):
		return "Start worker node."

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		threads: List[Popen] = []
		from requests import get
		my_ip = get("http://icanhazip.com").content.decode().strip()
		common_cockroach_args = ' '.join([
			"--insecure",
			f"--advertise-host={my_ip}"
		])
		from util.redis import get_network
		the_network = get_network()
		# If we have no neighbours, then we start CockroachDB as a single node.  More nodes can join later.
		if not the_network:
			cockroach_cmd = f"{COCKROACH_BINARY} start-single-node {common_cockroach_args}"
		elif my_ip < min(the_network):
			cockroach_cmd = f"{COCKROACH_BINARY} start-single-node {common_cockroach_args}"
		else:
			cockroach_cmd = f"{COCKROACH_BINARY} start {common_cockroach_args} --join={','.join(the_network)}"
		if not the_network:
			cockroach_cmd = f"{COCKROACH_BINARY} start-single-node {common_cockroach_args}"
		else:
			cockroach_active_on_ips: List[str] = []
			for ip in the_network:
				try:
					address = (ip, COCKROACH_PORT)
					s = socket(AF_INET, SOCK_STREAM)
					s.connect(address)
					s.shutdown(2)
					cockroach_active_on_ips.append(ip)
				except Exception:
					pass
				if len(cockroach_active_on_ips) == 3:
					break
			if len(cockroach_active_on_ips) > 0:
				cockroach_cmd = f"{COCKROACH_BINARY} start {common_cockroach_args} --join={','.join(cockroach_active_on_ips)}"
			else:
				lowest_ip = min(min(the_network), my_ip)
				if lowest_ip == my_ip:
					cockroach_cmd = f"{COCKROACH_BINARY} start-single-node {common_cockroach_args}"
				else:
					while not(cockroach_active_on_ips):
						time.sleep(0.3)
						for ip in the_network:
							try:
								address = (ip, COCKROACH_PORT)
								s = socket(AF_INET, SOCK_STREAM)
								s.connect(address)
								s.shutdown(2)
								cockroach_active_on_ips.append(ip)
							except Exception:
								pass
							if len(cockroach_active_on_ips) == 3:
								break
					cockroach_cmd = f"{COCKROACH_BINARY} start {common_cockroach_args} --join={','.join(cockroach_active_on_ips)}"
		services: Dict[str, Tuple[Optional[str], str]] = {
			"grobid": (
				GROBID_DIR_PATH,
				f"/usr/bin/sh {GROBID_EXEC_PATH} run"
			),
			GARAGE_BINARY_NAME: (
				None,
				f"{GARAGE_BINARY} server"
			),
			COCKROACH_BINARY_NAME: (
				None,
				cockroach_cmd
			),
		}
		print("Running services in TMUX...")
		for name, (cwd, cmd) in services.items():
			if call([TMUX_BINARY, "has-session", "-t", name]) != 0:
				threads.append(Popen([TMUX_BINARY, "new-session", "-d", "-s", name, cmd], cwd=cwd))
		wait_then_clear(threads)
		from user_actions.WorkerServer import WorkerServer
		WorkerServer().start()
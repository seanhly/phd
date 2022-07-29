from typing import List
from user_actions.UserAction import UserAction
from constants import GARAGE_BINARY, GARAGE_PORT, GARAGE_S3_PORT
from subprocess import call, check_output
from socket import socket, AF_INET, SOCK_STREAM
import time
from util.redis import await_garage_id, set_garage_id
from util.ssh_do import ssh_do


class ConnectGarageWorkers(UserAction):
	@classmethod
	def command(cls) -> str:
		return "cgws"

	@classmethod
	def description(cls):
		return "Connect up garage workers."

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		from util.redis import get_network
		the_network = get_network()
		if the_network:
			garage_active_on_ips: List[str] = []
			for ip in the_network:
				try:
					for port in (GARAGE_PORT, GARAGE_S3_PORT):
						address = (ip, port)
						s = socket(AF_INET, SOCK_STREAM)
						s.connect(address)
						s.shutdown(2)
					garage_active_on_ips.append(ip)
				except Exception:
					pass
				if len(garage_active_on_ips) == 3:
					break
			if len(garage_active_on_ips) == 0:
				while not(garage_active_on_ips):
					time.sleep(0.3)
					for ip in the_network:
						try:
							for port in (GARAGE_PORT, GARAGE_S3_PORT):
								address = (ip, port)
								s = socket(AF_INET, SOCK_STREAM)
								s.connect(address)
								s.shutdown(2)
							garage_active_on_ips.append(ip)
						except Exception:
							pass
						if len(garage_active_on_ips) == 3:
							break
				while True:
					try:
						for port in (GARAGE_PORT, GARAGE_S3_PORT):
							address = ("127.0.0.1", port)
							s = socket(AF_INET, SOCK_STREAM)
							s.connect(address)
							s.shutdown(2)
						break
					except Exception:
						pass
						time.sleep(0.3)
				set_garage_id(
					check_output(
						[GARAGE_BINARY, "node", "id", "-q"]
					).strip().split('@')[0]
				)
		connected = False
		for ip in garage_active_on_ips:
			try:
				garage_id = await_garage_id(ip)
				if call([
					GARAGE_BINARY,
					"node",
					"connect",
					f"{garage_id}@{ip}:{GARAGE_PORT}"
				]) == 0:
					connected = True
					break
			except:
				pass
		if not connected:
			raise "cannot connect"
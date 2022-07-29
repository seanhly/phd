from subprocess import Popen
from typing import List
from user_actions.UserAction import UserAction
from cloud.vendors.Vultr import Vultr
from constants import PHD_LABEL
from util.ssh_do import ssh_do


class Whitelist(UserAction):
	@classmethod
	def command(cls) -> str:
		return "wl"

	@classmethod
	def description(cls):
		return "Add an IP to the whitelist"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		vendor = Vultr
		instances = vendor.list_instances(label=PHD_LABEL)
		threads: List[Popen] = []
		ip = self.query.strip()
		cmd = f"/usr/sbin/ufw allow from {ip}"
		for i in instances:
			ssh_do(i.main_ip, cmd, threads)
		for thread in threads:
			thread.wait()

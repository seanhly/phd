from subprocess import Popen
from typing import List
from user_actions.UserAction import UserAction
from cloud.server.Pool import Pool
from cloud.vendors.Vultr import Vultr
from constants import INSTALL_SCRIPT, PHD_LABEL
from util.ssh_do import ssh_do


class UpdateAll(UserAction):
	@classmethod
	def command(cls) -> str:
		return "u"

	@classmethod
	def description(cls):
		return "Update all the deployed instances"

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
		Pool.load(vendor).update(instances)
		threads: List[Popen] = []
		for i in instances:
			print(i.main_ip)
			ssh_do(i.main_ip, INSTALL_SCRIPT, threads)
		for thread in threads:
			thread.wait()
from typing import Dict, Set
from user_actions.UserAction import UserAction
from cloud.server.Pool import Pool
from cloud.vendors.Vultr import Vultr
from constants import PHD_LABEL
import random
from worker_actions import WorkerAction

from util.ssh_do import ssh_do
random.seed(1)


class ControlPanel(UserAction):
	@classmethod
	def command(cls) -> str:
		return "ctrl"

	@classmethod
	def description(cls):
		return "Print information about server instances in HTML"

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
		print("<!doctype html>")
		print("<head>")
		print("<title>PhD Cluster Information</title>")
		print("<style>")
		print("""
		.haze {
			opacity: 0.7;
			font-size: xx-small;
		}
		td {
			text-align: center;
			margin: 0;
			padding: 0;
		}
		td>span {
			display: block;
			width: 100%;
			padding: 10px;
		}
		""")
		instance_ips: Set[str] = set(
			i.main_ip for i in instances
		)
		colours = {
			ip: "#" + ''.join([random.choice('0123456789abcdef') for j in range(6)])
			for ip in instance_ips
		}
		for ip in instance_ips:
			print(f"#id{ip.replace('.', '-')} {{")
			print(f"\tbackground-color: {colours[ip.strip()]};")
			print("}")
		print("</style>")
		print("<body>")
		print("<h1>PhD Cluster Information</h1>")
		right_of: Dict[str, str] = {}
		left_of: Dict[str, str] = {}
		right2_of: Dict[str, str] = {}
		left2_of: Dict[str, str] = {}
		for ip in instance_ips:
			r2, r, l, l2 = (
				ssh_do(
					ip,
					"/usr/bin/redis-cli",
					None,
					"mget R2 R L L2",
					stdout=True,
				)
					.stdout
					.read()
					.decode()
					.strip()
					.split()
			)
			right_of[ip] = r
			left_of[ip] = l
			right2_of[ip] = r2
			left2_of[ip] = l2
		first_ip = [i for i in instance_ips][0]
		next_ip = right_of[first_ip]
		ordered_ips = [first_ip]
		while next_ip != first_ip:
			ordered_ips.append(next_ip)
			next_ip = right_of[next_ip]
		queue_names = [
			c.queue_name()
			for c in WorkerAction.__subclasses__()
		]
		hlen_commands = [
			f"hlen {q}"
			for q in queue_names
		]
		disk = {
			ip: ssh_do(
					ip,
					"/usr/bin/df -B1 /",
					stdout=True,
				)
					.stdout
					.read()
					.decode()
					.strip()
					.split("\n")[-1]
					.split()[2:4]
			for ip in instance_ips
		}
		queue_lengths = {
			ip: dict(
				zip(
					queue_names,
					ssh_do(
						ip,
						"/usr/bin/redis-cli -n 1",
						stdin=hlen_commands,
						stdout=True,
					)
						.stdout
						.read()
						.decode()
						.strip()
						.split()
				)
			)
			for ip in instance_ips
		}
		print("<table>")
		print("<tr class=haze>")
		print("<td>L2</td>")
		for s in ordered_ips:
			ip = left2_of[s]
			print("<td>")
			print(f"<span id='id{ip.replace('.', '-')}'>{ip}</span>")
		print("</tr>")
		print("<tr class=haze>")
		print("<td>L1</td>")
		for s in ordered_ips:
			ip = left_of[s]
			print("<td>")
			print(f"<span id='id{ip.replace('.', '-')}'>{ip}</span>")
		print("</tr>")
		print("<tr>")
		print("<td>Worker</td>")
		for ip in ordered_ips:
			print("<td>")
			print(f"<span id='id{ip.replace('.', '-')}'>{ip}</span>")
		print("</tr>")
		print("<tr class=haze>")
		print("<td>R1</td>")
		for s in ordered_ips:
			ip = right_of[s]
			print("<td>")
			print(f"<span id='id{ip.replace('.', '-')}'>{ip}</span>")
		print("</tr>")
		print("<tr class=haze>")
		print("<td>R2</td>")
		for s in ordered_ips:
			ip = right2_of[s]
			print("<td>")
			print(f"<span id='id{ip.replace('.', '-')}'>{ip}</span>")
		print("</tr>")
		for q in queue_names:
			print("<tr>")
			print(f"<td>{q}</td>")
			for ip in ordered_ips:
				l = queue_lengths[ip][q]
				print(f"<td>{l}</td>")
			print("</tr>")
		for index, name in {0: "Disk Used", 1: "Disk Available"}.items():
			print("<tr>")
			print(f"<td>{name}</td>")
			for ip in ordered_ips:
				b = disk[ip][index]
				print(f"<td>{b}</td>")
			print("</tr>")

		print("</table>")
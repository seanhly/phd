import subprocess
from typing import List, Optional, Set

from JSON import JSON
from cloud.Vendor import Vendor
from cloud.server.Instance import Instance
from cloud.server.OperatingSystem import OperatingSystem
from cloud.server.Plan import Plan
from cloud.server.Region import Region
from cloud.server.SSHKey import SSHKey
import re
from constants import POOL_LABEL

t = "A5D76NVGTEMR56WYGM252PYOQZWIBK52D2OA"


def lowest_cost_per_disk(plan: Plan):
	return (plan.disk * plan.disk_count) / plan.monthly_cost

def os_family_name_then_version(os: OperatingSystem):
	key = [os.family, *(os.name.split())]
	if len(key) >= 3:
		if re.fullmatch("[0-9]+(\.[0-9]+)?", key[2]):
			key[2] = -float(key[2])
		else:
			key.insert(2, 9e99)
	return tuple(key)


class Vultr(Vendor):
	@classmethod
	def list_regions(cls):
		regions = [
			region
			for region in (
				Region(r, cls)
				for r in JSON.loads(
					subprocess.check_output(
						[
							"/usr/bin/curl",
							'https://api.vultr.com/v2/regions?per_page=500',
							"-H",
							f"Authorization: Bearer {t}",
						],
						stderr=subprocess.DEVNULL
					).decode()
				)["regions"]
			)
		]

		return regions

	@classmethod
	def list_plans(
		cls,
		min_ram = 0,
		max_cost = 9e99,
		sort_by = lowest_cost_per_disk,
		region: Region = None
	):
		plans = [
			plan
			for plan in (
				Plan(p, cls)
				for p in JSON.loads(
					subprocess.check_output(
						[
							"/usr/bin/curl",
							'https://api.vultr.com/v2/plans?per_page=500',
							"-H",
							f"Authorization: Bearer {t}",
						],
						stderr=subprocess.DEVNULL
					).decode()
				)["plans"]
			)
			if (
				plan.monthly_cost <= max_cost
				and plan.ram >= min_ram
				and (not region or region.id in plan.locations)
			)
		]
		plans.sort(key=sort_by)

		return plans

	@classmethod
	def list_operating_systems(
		cls,
		os_family: Optional[str] = None,
		sort_by = os_family_name_then_version,
		in_name: Set[str] = set(),
	):
		operating_systems = [
			os for os in (
				OperatingSystem(o, cls)
				for o in JSON.loads(
					subprocess.check_output(
						[
							"/usr/bin/curl",
							'https://api.vultr.com/v2/os?per_page=500',
							"-H",
							f"Authorization: Bearer {t}",
						],
						stderr=subprocess.DEVNULL
					).decode()
				)["os"]
			)
			if (
				(not os_family or os.family == os_family)
				and all(substr in os.name for substr in in_name)
			)
		]
		operating_systems.sort(key=sort_by)

		return operating_systems

	@classmethod
	def list_ssh_keys(cls):
		return [
			SSHKey(k, cls)
			for k in JSON.loads(
				subprocess.check_output(
					[
						"/usr/bin/curl",
						'https://api.vultr.com/v2/ssh-keys?per_page=500',
						"-H",
						f"Authorization: Bearer {t}",
					],
					stderr=subprocess.DEVNULL
				).decode()
			)["ssh_keys"]
		]

	@classmethod
	def list_instances(cls, label: Optional[str] = None):
		return [
			instance
			for instance in (
				Instance(i, cls)
				for i in JSON.loads(
					subprocess.check_output(
						[
							"/usr/bin/curl",
							'https://api.vultr.com/v2/instances?per_page=500',
							"-H",
							f"Authorization: Bearer {t}",
						],
						stderr=subprocess.DEVNULL
					).decode()
				)["instances"]
			)
			if (not label or label == instance.label)
		]

	@classmethod
	def create_instance(
		cls,
		region: Region = None,
		plan: Plan = None,
		os: OperatingSystem = None,
		sshkey: SSHKey = None,
	):
		if not region:
			from cloud.server.Regions import Regions
			region = Regions.nearest_region()
		if not plan:
			from cloud.server.Plans import Plans
			plan = Plans.cheapest_plan(region=region)
		if not os:
			from cloud.server.OperatingSystems import OperatingSystems
			os = OperatingSystems.default_os()
		if not sshkey:
			from cloud.server.SSHKeys import SSHKeys
			sshkey = SSHKeys.default_ssh_key()
		return Instance(
			JSON.loads(subprocess.check_output(
				[
					"/usr/bin/curl",
					'https://api.vultr.com/v2/instances?per_page=500',
					"-X",
					"POST",
					"-H",
					f"Authorization: Bearer {t}",
					"-H",
					"Content-Type: application/json",
					"--data",
					JSON.dumps(
						dict(
							region=region.id,
							plan=plan.id,
							label=POOL_LABEL,
							os_id=os.id,
							backups="disabled",
							sshkey_id=[sshkey.id],
						)
					),
				],
				stderr=subprocess.DEVNULL
			).decode()),
			vendor=cls,
		)

	@classmethod
	def destroy_instance(cls, id: str):
		print(subprocess.check_output(
			[
				"/usr/bin/curl",
				f"https://api.vultr.com/v2/instances/{id}",
				"-X",
				"DELETE",
				"-H",
				f"Authorization: Bearer {t}",
			],
			stderr=subprocess.DEVNULL
		).decode())
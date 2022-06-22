from cloud.vendors.Vultr import Vultr


class OperatingSystems:
	def default_os():
		return Vultr.list_operating_systems(
			os_family="ubuntu",
			in_name={"LTS"}
		)[0]
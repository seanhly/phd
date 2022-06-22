from cloud.vendors.Vultr import Vultr

# Popular
PREFER_UBUNTU = dict(
	os_family="ubuntu",
	in_name={"LTS"}
)

# Lightweight
PREFER_ARCH = dict(
	os_family="archlinux",
)


class OperatingSystems:
	def default_os():
		options = Vultr.list_operating_systems(**PREFER_UBUNTU)
		return options[0] # Give me the newest version of the above.
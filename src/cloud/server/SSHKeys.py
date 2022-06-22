from cloud.vendors.Vultr import Vultr


class SSHKeys:
	@classmethod
	def default_ssh_key(cls, **kwargs):
		return Vultr.list_ssh_keys(**kwargs)[0]
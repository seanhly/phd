from genericpath import exists
from cloud.vendors.Vultr import Vultr
from constants import PHD_PRIVATE_RSA_KEY, PHD_PUBLIC_RSA_KEY, USER
import subprocess


class SSHKeys:
	@classmethod
	def default_ssh_key(cls, **kwargs):
		with open("/etc/hostname", "r") as f:
			hostname = f.read().strip()
		name = f"phd_{hostname}_{USER}"
		if exists(PHD_PUBLIC_RSA_KEY):
			with open(PHD_PUBLIC_RSA_KEY, "r") as f:
				local_ssh = f.read().strip()
			remote_ssh_key = None
			remote_keys = Vultr.list_ssh_keys(**kwargs)
			i = 0
			while i < len(remote_keys) and not remote_ssh_key:
				ssh_key = remote_keys[i]
				if ssh_key.name == name:
					remote_ssh_key = ssh_key
					if ssh_key.ssh_key.strip() == local_ssh:
						return ssh_key
				i += 1
		else:
			remote_ssh_key = None
			subprocess.Popen(
				[
					"/usr/bin/ssh-keygen",
					"-P",
					"",
					"-f",
					PHD_PRIVATE_RSA_KEY,
				]
			).wait()
			with open(PHD_PUBLIC_RSA_KEY, "r") as f:
				local_ssh = f.read().strip()
		if remote_ssh_key:
			Vultr.patch_ssh_key(remote_ssh_key.id, name, local_ssh)
			return remote_ssh_key
		else:
			return Vultr.create_ssh_key(name, local_ssh)
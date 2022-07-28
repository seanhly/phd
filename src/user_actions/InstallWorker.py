from typing import Dict, List, Optional, Tuple
from user_actions.UserAction import UserAction
from time import sleep
from constants import (
	APT_GET_BINARY, COCKROACH_BINARY, COCKROACH_BINARY_NAME, COCKROACH_INSTALL_URL,
	GARAGE_BINARY, GARAGE_BINARY_NAME, GARAGE_INSTALL_URL, GROBID_DIR_PATH,
	GROBID_EXEC_PATH, GROBID_SOURCE, PACMAN_BINARY, RSYNC_BINARY,
	SERVICE_BINARY, SSH_CLIENT, SYSTEMCTL_BINARY, TMP_DIR, UFW_BINARY,
	WORKING_DIR, TMUX_BINARY
)
from os import makedirs, walk, chmod
from os.path import exists, join, basename
from shutil import move, rmtree
from subprocess import Popen, call
from zipfile import ZipFile
from io import BytesIO
from urllib.request import urlopen, Request
from tarfile import open
from re import sub
from util.wait_then_clear import wait_then_clear


class InstallWorker(UserAction):
	@classmethod
	def command(cls) -> str:
		return "install"

	@classmethod
	def description(cls):
		return "Install/start worker node software."

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
		threads.append(Popen([UFW_BINARY, "allow", "from", SSH_CLIENT]))
		if exists(APT_GET_BINARY):
			deb_dependencies = [
				"default-jre",
				"tmux",
				"nginx",
				"redis",
				"transmission-daemon",
				"python3-redis",
				"python3-dateparser",
			]
			def deb_install() -> int:
				return call([APT_GET_BINARY, "-y", "install", *deb_dependencies])
			while deb_install() != 0:
				sleep(1)
		elif exists(PACMAN_BINARY):
			pacman_dependencies = [
				"jre11-openjdk-headless",
				"tmux",
				"nginx",
				"redis",
				"transmission-daemon",
				"python-redis",
				"python-requests",
				"python-dateparser",
			]
			threads.append(
				Popen([
					PACMAN_BINARY,
					"-S",
					*pacman_dependencies
				])
			)
		threads.append(Popen(["pip3", "install", "grobid-tei-xml"]))
		# Wait for installations, firewall changes.
		wait_then_clear(threads)
		services = ["nginx", "redis-server", "transmission-daemon"]
		for service in services:
			threads.append(Popen([SYSTEMCTL_BINARY, "enable", service]))
		threads.append(Popen([RSYNC_BINARY, "-a", "/phd/etc", "/"]))
		# Wait for config writes and service enabling.
		wait_then_clear(threads)
		rmtree("/phd")
		for service in services:
			threads.append(Popen([SERVICE_BINARY, service, "restart"]))
		# Wait for service restarts.
		wait_then_clear(threads)
		if not exists(WORKING_DIR):
			makedirs(WORKING_DIR)
		from requests import get
		if not exists(GROBID_EXEC_PATH):
			print("Downloading and unzipping GROBID...")
			ZipFile(
				BytesIO(
					get(GROBID_SOURCE).content
				)
			).extractall(WORKING_DIR)
			print("Setting GROBID permissions...")
			for path, _, files in walk(GROBID_DIR_PATH):
				for file in files:
					file_path = join(path, file)
					chmod(file_path, 0o700)
		if not exists(COCKROACH_BINARY):
			print("Downloading and untarring CockroachDB...")
			req = Request(COCKROACH_INSTALL_URL)
			with urlopen(req) as f:
				with open(fileobj=f, mode='r|*') as tar:
					# The tar appears to contain a directory resembling the
					# final part of the URL.
					cockroach_extracted_dir_name = sub(
						"(\.[a-zA-Z]+)+$",
						"",
						basename(COCKROACH_INSTALL_URL),
					)
					tar.extractall(TMP_DIR)
			cockroach_extracted_dir_path = join(TMP_DIR, cockroach_extracted_dir_name)
			cockroach_binary_src = join(cockroach_extracted_dir_path, COCKROACH_BINARY_NAME)
			move(cockroach_binary_src, COCKROACH_BINARY)
			rmtree(cockroach_extracted_dir_path)
			chmod(COCKROACH_BINARY, 0o700)
		if not exists(GARAGE_BINARY):
			print("Downloading Garage...")
			with open(GARAGE_BINARY, "wb") as f:
				f.write(get(GARAGE_INSTALL_URL).content)
			chmod(GARAGE_BINARY, 0o700)
		my_ip = get("http://icanhazip.com").content.decode().strip()
		common_cockroach_args = ' '.join([
			"--insecure",
			"--advertise-host={my_ip}"
		])
		from util.redis import get_network
		neighbours = set(get_network().values())
		# If we have no neighbours, then we start CockroachDB as a single node.  More nodes can join later.
		if neighbours == {my_ip}:
			cockroach_cmd = f"{COCKROACH_BINARY} start-single-node {common_cockroach_args}"
		else:
			cockroach_cmd = f"{COCKROACH_BINARY} start {common_cockroach_args} --join={','.join(neighbours)}"
		services: Dict[str, Tuple[Optional[str], str]] = {
			"grobid": (GROBID_DIR_PATH, f"/usr/bin/sh {GROBID_EXEC_PATH} run"),
			GARAGE_BINARY_NAME: (None, f"{GARAGE_BINARY} server"),
			COCKROACH_BINARY_NAME: (None, cockroach_cmd),
		}
		print("Running services in TMUX...")
		for name, (cwd, cmd) in services.items():
			if call([TMUX_BINARY, "has-session", "-t", name]) != 0:
				threads.append(Popen([TMUX_BINARY, "new-session", "-d", "-s", name, cmd], cwd=cwd))
		wait_then_clear(threads)
		from user_actions.WorkerServer import WorkerServer
		WorkerServer().start()
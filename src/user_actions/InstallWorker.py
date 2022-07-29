from typing import List
from user_actions.UserAction import UserAction
from time import sleep
from constants import (
	APT_GET_BINARY, COCKROACH_BINARY, COCKROACH_BINARY_NAME, COCKROACH_INSTALL_URL,
	GARAGE_BINARY, GARAGE_INSTALL_URL, GIT_BINARY, GIT_SOURCE, GROBID_DIR_PATH,
	GROBID_EXEC_PATH, GROBID_SOURCE, PACMAN_BINARY, PHD_ETC_DIR, PHD_GIT_DIR, RSYNC_BINARY,
	SERVICE_BINARY, SSH_CLIENT, SYSTEMCTL_BINARY, TMP_DIR, UFW_BINARY,
	WORKING_DIR
)
from os import makedirs, walk, chmod
from os.path import exists, join, basename
from shutil import move, rmtree
from subprocess import Popen, call
from zipfile import ZipFile
from io import BytesIO
from urllib.request import urlopen, Request
import tarfile
from re import sub
from util.wait_then_clear import wait_then_clear


class InstallWorker(UserAction):
	@classmethod
	def command(cls) -> str:
		return "install"

	@classmethod
	def description(cls):
		return "Install worker node software."

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
		if not exists(PHD_GIT_DIR):
			threads.append(Popen([GIT_BINARY, "clone", GIT_SOURCE]))
		# Wait for installations, firewall changes, git clone.
		wait_then_clear(threads)
		services = ["nginx", "redis-server", "transmission-daemon"]
		for service in services:
			threads.append(Popen([SYSTEMCTL_BINARY, "enable", service]))
		threads.append(Popen([RSYNC_BINARY, "-a", PHD_ETC_DIR, "/"]))
		# Wait for config writes and service enabling.
		wait_then_clear(threads)
		rmtree(PHD_GIT_DIR)
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
				with tarfile.open(fileobj=f, mode='r|*') as tar:
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
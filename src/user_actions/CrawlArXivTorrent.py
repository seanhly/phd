from user_actions.UserAction import UserAction
from requests import get
import subprocess
import re
from os import unlink
import time


ID = "ID"
DONE = "Done"
HAVE = "Have"
ETA = "ETA"
UP = "Up"
DOWN = "Down"
RATIO = "Ratio"
STATUS = "Status"
NAME = "Name"


class CrawlArXivTorrent(UserAction):
	@classmethod
	def command(cls) -> str:
		return "crawl-arxiv-torrent"

	@classmethod
	def description(cls):
		return "Crawl arXiv torrent from archive.org"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		if self.query:
			id = self.query.strip()
			torrent_url = f"https://archive.org/download/{id}/{id}_archive.torrent"
			print(torrent_url)
			torrent_file_path = "torrent.torrent"
			with open(torrent_file_path, "wb") as torrent_file:
				torrent_file.write(get(torrent_url).content)
			output = subprocess.run(
				["/usr/bin/transmission-remote", "-a", torrent_file_path],
				stderr=subprocess.DEVNULL,
			)
			output.check_returncode()
			unlink(torrent_file_path)
			in_progress = True
			while in_progress:
				transmission_output = subprocess.check_output(
					["/usr/bin/transmission-remote", "-l"],
					stderr=subprocess.DEVNULL,
				).decode()
				header, *lines, summary = [
					re.split("\s{2,}", line.strip(), 9)
					for line in transmission_output.strip().split("\n")
				]
				indices = {
					column: header.index(column)
					for column in (
						ID, DONE, HAVE, ETA, UP, DOWN, RATIO, STATUS, NAME,
					)
				}
				in_progress = False
				for line in lines:
					transmission_name = line[indices[NAME]]
					in_progress = transmission_name == id
					if in_progress:
						transmission_id = int(line[indices[ID]])
						percentage_str = line[indices[DONE]]
						status = line[indices[STATUS]]
						eta = line[indices[ETA]]
						if percentage_str == "n/a":
							percentage = 0
						else:
							percentage = float(percentage_str[:-1]) / 100
						print(transmission_id, percentage, status, eta, transmission_name)
						if percentage == 1.0 and eta == "Done":
							transmission_output = subprocess.check_output(
								["/usr/bin/transmission-remote", "-t", str(transmission_id), "-r"],
								stderr=subprocess.DEVNULL,
							).decode()
							print(transmission_output)
						break
				time.sleep(2)
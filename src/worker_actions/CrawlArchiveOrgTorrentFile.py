from requests import get
import re

from worker_actions.WorkerAction import WorkerAction


class CrawlArchiveOrgTorrentFile(WorkerAction):
	id: str

	def __init__(self, input: bytes):
		self.id = input.decode().strip()

	@classmethod
	def queue_name(cls) -> str:
		return "crawl-archive.org-torrent-file"

	@classmethod
	def description(cls) -> str:
		return "Crawl an archive.org torrent file."

	def execute(self):
		print("TODO")
		return ()
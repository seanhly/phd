from requests import get
import re
from worker_actions.DistributeArchiveOrgTorrentWork import DistributeArchiveOrgTorrentWork

from worker_actions.WorkerAction import WorkerAction


class CrawlArchiveOrgTorrentListPage(WorkerAction):
	page: int

	def __init__(self, input: bytes):
		self.page = int(input.decode().strip())

	@classmethod
	def queue_name(cls) -> str:
		return "archive.org-torrent-list-page"

	@classmethod
	def description(cls) -> str:
		return "Crawl an archive.org torrent list page for torrent links."

	def execute(self):
		page_url = f"https://archive.org/details/arxiv-bulk?page={self.page}"
		page_content = get(page_url).content.decode()
		page_ids = set(
			link[len('"/details/'):-1]
			for link in
			re.findall('("/details/arXiv_[^"]+")', page_content)
		)
		next_pages = [
			f"{self.page * 2}",
			f"{self.page * 2 + 1}",
		]
		if page_ids:
			return (
				(self, next_pages),
				(DistributeArchiveOrgTorrentWork, page_ids),
			)
		else:
			return ()

	@classmethod
	def one_at_a_time(cls) -> bool:
		True
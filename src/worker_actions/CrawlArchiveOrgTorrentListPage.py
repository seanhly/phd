import re
from worker_actions.WorkerAction import WorkerAction


class CrawlArchiveOrgTorrentListPage(WorkerAction):
	page: int

	def __init__(self, the_input: bytes):
		self.page = int(the_input.decode().strip())

	@classmethod
	def queue_name(cls) -> str:
		return "archive.org-torrent-list-page"

	@classmethod
	def description(cls) -> str:
		return "Crawl an archive.org torrent list page for torrent links."

	def execute(self):
		page_url = f"https://archive.org/details/arxiv-bulk?page={self.page}"
		from requests import get
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
			)
		else:
			return ()

	@classmethod
	def one_at_a_time(cls) -> bool:
		return True

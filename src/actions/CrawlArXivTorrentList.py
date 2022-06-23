from actions.Action import Action
from cloud.server.Pool import Pool
from cloud.vendors.Vultr import Vultr
from requests import get
import re


class CrawlArXivTorrentList(Action):
	@classmethod
	def command(cls) -> str:
		return "crawl-arxiv-archive"

	@classmethod
	def description(cls):
		return "Crawl the arXiv dataset on archive.org"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		id_set = set()
		new_ids = True
		page = 1
		while new_ids:
			page_content = get(f"https://archive.org/details/arxiv-bulk?page={page}").content.decode()
			#page_ids = set(re.findall("(arXiv_(?:pdf|src)_[0-9_]+)", page_content))
			page_ids = set(re.findall('("/details/arXiv_[^"]+")', page_content))
			new_ids = False
			for link in page_ids:
				id = link[len('"/details/'):-1]
				if id not in id_set:
					id_set.add(id)
					new_ids = True
					print(id)
			page += 1
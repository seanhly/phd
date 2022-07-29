from user_actions.UserAction import UserAction
from cloud.server.Pool import Pool
from cloud.vendors.Vultr import Vultr
from os.path import exists
import subprocess


class ParseAcademicPDF(UserAction):
	@classmethod
	def command(cls) -> str:
		return "parse"

	@classmethod
	def description(cls):
		return "Parse an academic PDF using the GROBID cluster"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		pool = Pool.load(Vultr)
		grobid_ip = pool.pool[0].main_ip
		if self.query:
			if exists(self.query):
				print(grobid_ip)
				tei_str = subprocess.check_output(
					[
						"/usr/bin/curl",
						"-s",
						"--form",
						f"input=@\"{self.query}\"",
						"-X",
						"POST",
						f"http://{grobid_ip}/grobid/api/processFulltextDocument",
					],
					stderr=subprocess.DEVNULL
				).decode()
				print(tei_str)
				import grobid_tei_xml
				tei = grobid_tei_xml.parse_document_xml(tei_str).to_dict()
				print(tei)

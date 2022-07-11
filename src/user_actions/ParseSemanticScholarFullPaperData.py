from user_actions.UserAction import UserAction
from os.path import exists
from data.SemanticScholarArticle import SemanticScholarArticle

class ParseSemanticScholarFullPaperData(UserAction):
	@classmethod
	def command(cls) -> str:
		return "ss"

	@classmethod
	def description(cls):
		return "Parse JSON data from semantic scholar's 'full paper' corpus."

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		path = self.query.strip()
		if exists(path):
			with open(path, "r") as f:
				for line in f:
					ssa = SemanticScholarArticle(line)
					print(ssa)
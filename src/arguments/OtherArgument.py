from arguments.Argument import Argument
import re


class OtherArgument(Argument):
	argument: str

	def __init__(self, argument: str, _=None):
		self.argument = argument

	def __str__(self) -> str:
		return self.argument

	def parse_argument_for_action(self, _, current_index, action):
		if self.argument:
			prefix_match = re.fullmatch("^([^\\s:]+:)(.*\\s.*)", self.argument)
			if prefix_match:
				processed_argument = f"{prefix_match[1]}\"{prefix_match[2]}\""
			elif re.search("\\s", self.argument):
				processed_argument = f"\"{self.argument}\""
			else:
				processed_argument = self.argument
			action.query_parts.append(processed_argument)
		return current_index + 1

	@classmethod
	def fits(cls, s: str) -> bool:
		return True

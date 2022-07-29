from arguments.Argument import Argument
import re


class IPArgument(Argument):
	ip: str

	def __init__(self, ip: str, _ = None):
		# Trim off the leading double-hyphen.
		self.ip = ip

	def __str__(self):
		return self.option

	def parse_argument_for_action(self, _, current_index, action):
		action.ip_arguments.add(self)
		return current_index + 1
			
	@classmethod
	def fits(cls, s: str) -> bool:
		if not s:
			return False
		parts = s.split(".")
		if len(parts) != 4:
			return False
		for p in parts:
			if not re.fullmatch("[0-9]+", p):
				return False
			i = int(p)
			if i < 0 or i > 255:
				return False
		return True
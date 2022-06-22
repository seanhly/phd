from typing import Dict, Set
from arguments.Argument import Argument
import re


class OptionArgument(Argument):
	option: str

	def __init__(self, option: str, _ = None):
		# Trim off the leading double-hyphen.
		self.option = option[2:]

	def __str__(self):
		return self.option

	def parse_argument_for_action(self, arguments, current_index, action):
		current_index += 1
		if self.option in action.disqualified_options:
			action.conflicting_options[self.option] = action.indexed_blocking_options()[self.option]
		if self.option not in action.recognised_options():
			action.unrecognised_options.add(self.option)
		else:
			action.options[self.option] = None
			if self.option in action.indexed_obligatory_option_groups():
				for o in action.indexed_obligatory_option_groups()[self.option]:
					del action.indexed_obligatory_option_groups()[o]
			if self.option in action.indexed_blocking_options():
				for o in action.indexed_blocking_options()[self.option]:
					action.disqualified_options[o] = self.option
			if self.option in action.arg_options():
				if current_index >= len(arguments):
					action.missing_argument_for_options.append(self.option)
				else:
					argument = arguments[current_index]
					if type(argument) == type(self):
						action.missing_argument_for_options.append(self.option)
					elif type(argument) != action.arg_options()[self.option]:
						current_index += 1
						action.incorrect_argument_type_for_options.append((self.option, argument))
					else:
						current_index += 1
						action.options[self.option] = argument

		return current_index
			
	@classmethod
	def fits(cls, s: str) -> bool:
		return re.fullmatch("--.*", s)
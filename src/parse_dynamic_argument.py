from typing import List, Type
from arguments.Argument import Argument
from arguments.OtherArgument import OtherArgument
from arguments.OptionArgument import OptionArgument

def parse_dynamic_argument(argument: str, action: str):
	argument_types: List[Type[Argument]] = [
		OptionArgument,
		OtherArgument,
	]
	for T in argument_types:
		if T.fits(argument):
			return T(argument, action)
	return None
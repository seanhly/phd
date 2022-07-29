from abc import ABC, abstractmethod
from typing import List


class Argument(ABC):
	@abstractmethod
	def __str__(self) -> str:
		pass

	@abstractmethod
	def parse_argument_for_action(
		self,
		arguments: List["Argument"],
		current_index: int,
		action,
	) -> int:
		return current_index + 1

	@classmethod
	@abstractmethod
	def fits(cls, s: str) -> bool:
		return False

	@abstractmethod
	def __init__(self, text: str, action: str = None):
		pass
